"""
数据库模块
数据读取、解析逻辑（对应"db数据解释/读取"）
"""
import os
import re
import logging
from typing import List, Dict, Optional, Tuple
from datetime import date
from app.domain.entities import LogEntry, ItemInfo, DurationInfo, LogAnalysisResult, ConfigGroup
from app.infrastructure.utils import parse_timestamp_to_seconds
from app.infrastructure.database import DatabaseManager

logger = logging.getLogger('BetterGI初始化')

# 需要过滤的物品列表
FORBIDDEN_ITEMS = ['调查', '直接拾取']

# 预编译正则表达式
FIRST_LINE_PATTERN = re.compile(r'^\[([^]]+)\] \[([^]]+)\] ([^\n]+)\n?([^\n[]*)\n')  # 匹配日志第一行
LOG_PATTERN = re.compile(r'\n\[([^]]+)\] \[([^]]+)\] ([^\n]+)\n?([^\n[]*)\n')  # 匹配日志行
TASK_BEGIN_PATTERN = re.compile(r'^配置组 "([^"]*)" 加载完成，共(\d+)个脚本，开始执行$')  # 匹配配置组开始


class LogDataManager:
    """
    日志数据管理器
    负责日志文件的读取、解析和数据管理，集成SQLite数据库存储
    """
    
    def __init__(self, log_dir: str):
        """
        初始化日志数据管理器
        
        Args:
            log_dir: 日志目录路径
        """
        self.log_dir = log_dir
        self.item_cached_list = []  # 用于替代原有的筛选功能，避免物品的重复记录
        self.item_datadict = {
            '物品名称': [], '时间': [], '日期': [], '归属配置组': []
        }
        self.duration_datadict = {
            '日期': [], '持续时间': []
        }
        self.log_list = None
        
        # 初始化数据库管理器
        db_path = os.path.join(log_dir, 'CanLiangData.db')
        self.db_manager = DatabaseManager(db_path)
        
        # 今天的日期字符串，用于排除今天的数据存储
        self.today_str = date.today().strftime('%Y%m%d')
    
    def parse_log(self, log_content: str, date_str: str) -> LogAnalysisResult:
        """
        解析日志内容，提取日志类型、交互物品等信息，并统计相关信息。
        支持多次主窗体实例化/退出，自动计算所有段的总时长。

        Args:
            log_content: 日志文件内容
            date_str: 日期字符串

        Returns:
            LogAnalysisResult: 包含解析结果的分析结果对象
        """
        matches = LOG_PATTERN.findall(log_content)
        first_line_match = FIRST_LINE_PATTERN.match(log_content)
        if first_line_match:
            matches = [first_line_match.groups()] + matches

        item_count = {}
        items = []

        # 使用时间段列表管理所有活动时间段
        time_segments = []  # 存储所有时间段 [(start, end), ...]
        current_start = None
        last_time = None
        current_task = None  # 当前运行的配置组
        
        for match in matches:
            timestamp = match[0]  # 时间戳
            # level = match[1]  # 日志级别
            # log_type = match[2]  # 类名
            details = match[3].strip()  # 日志内容文本

            # 过滤禁用的关键词
            if any(keyword in details for keyword in FORBIDDEN_ITEMS):
                continue

            # 匹配配置组开始
            task_matches = TASK_BEGIN_PATTERN.match(details)
            if task_matches:
                current_task = task_matches.group(1)
            # 匹配配置组结束
            if current_task and f'配置组 "{current_task}" 执行结束' in details:
                current_task = None

            # 转换时间戳
            try:
                current_time = parse_timestamp_to_seconds(timestamp)
            except Exception as e:
                logger.error(f"解析时间戳{timestamp}时候发生错误:{e}")
                logger.error(f'涉及的完整匹配字符串：{match}')
                continue
                
            # 提取拾取内容
            if '交互或拾取' in details:
                item_name = details.split('：')[1].strip('"')
                item_count[item_name] = item_count.get(item_name, 0) + 1

                # 检查是否存在匹配的行
                cache_key = f'{item_name}{timestamp}{date_str}{current_task}'
                if cache_key not in self.item_cached_list:
                    item_info = ItemInfo(
                        name=item_name,
                        timestamp=timestamp,
                        date=date_str,
                        config_group=str(current_task) if current_task else None
                    )
                    items.append(item_info)
                    self.item_cached_list.append(cache_key)

            # 处理时间段
            if last_time is None:
                # 第一个事件
                current_start = current_time
            elif current_time - last_time > 300:
                # 间隔过大（超过5分钟），结束当前段
                if current_start is not None:
                    time_segments.append((current_start, last_time))
                current_start = current_time
            
            last_time = current_time

        # 处理最后一段
        if current_start is not None and last_time is not None:
            time_segments.append((current_start, last_time))

        # 计算总持续时间
        duration = sum(int(end - start) for start, end in time_segments)

        return LogAnalysisResult(
            item_count=item_count,
            duration=duration,
            items=items
        )

    def read_log_file(self, file_path: str, date_str: str) -> Optional[LogAnalysisResult]:
        """
        读取指定路径的日志文件并解析内容。

        Args:
            file_path: 日志文件路径
            date_str: 日期字符串

        Returns:
            Optional[LogAnalysisResult]: 解析后的日志信息对象，若发生错误则返回None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                log_content = file.read()
            return self.parse_log(log_content, date_str)
        except FileNotFoundError:
            logger.error(f"文件未找到: {file_path}")
            return None
        except Exception as e:
            logger.error(f"读取文件 {file_path} 时发生未知错误: {e}")
            return None

    def get_log_list(self) -> List[str]:
        """
        获取日志文件列表，并过滤掉不包含交互物品的日志文件。
        使用智能加载策略：优先从数据库读取，然后补充缺失的文件数据
        更新duration_datadict, item_datadict两个实例变量

        Returns:
            List[str]: 过滤后的日志文件名列表
        """
        # 获取所有以'better-genshin-impact'开头的日志文件，并提取日期部分
        log_files = [f.replace('better-genshin-impact', '').replace('.log', '')
                     for f in os.listdir(self.log_dir)
                     if f.startswith('better-genshin-impact')]

        # 获取数据库中已存储的日期
        stored_dates = set(self.db_manager.get_stored_dates())
        
        # 找出需要处理的文件（数据库中没有的或者是今天的文件）
        files_to_process = []
        for file_date in log_files:
            if file_date not in stored_dates or file_date == self.today_str:
                files_to_process.append(file_date)

        # 处理需要解析的文件
        new_data_processed = False
        for file_date in files_to_process:
            file_path = os.path.join(self.log_dir, f"better-genshin-impact{file_date}.log")
            result = self.read_log_file(file_path, file_date)
            if not result:
                continue

            # 过滤掉不需要的物品
            items = result.item_count.copy()
            for forbidden_item in FORBIDDEN_ITEMS:
                if forbidden_item in items:
                    del items[forbidden_item]

            # 只处理有物品的日志
            if items:
                # 如果不是今天的数据，存储到数据库
                if file_date != self.today_str:
                    item_list = [
                        {
                            'name': item.name,
                            'timestamp': item.timestamp,
                            'config_group': item.config_group
                        }
                        for item in result.items
                    ]
                    self.db_manager.insert_log_file_data(file_date, result.duration, item_list)
                
                new_data_processed = True

        # 从数据库加载所有数据（排除今天）
        duration_data = self.db_manager.get_duration_data(exclude_today=True)
        item_data = self.db_manager.get_item_data(exclude_today=True)
        
        # 如果今天有数据，单独处理今天的数据并合并
        today_file_path = os.path.join(self.log_dir, f"better-genshin-impact{self.today_str}.log")
        self.item_cached_list = [] # 清空缓存。因为在上一步骤中包含了今天的缓存数据。
        # 需要清空缓存数据
        if os.path.exists(today_file_path):
            today_result = self.read_log_file(today_file_path, self.today_str)
            if today_result:
                # 过滤掉不需要的物品
                today_items = today_result.item_count.copy()
                for forbidden_item in FORBIDDEN_ITEMS:
                    if forbidden_item in today_items:
                        del today_items[forbidden_item]
                
                # 如果今天有有效物品，添加到结果中
                if today_items:
                    # 将今天的数据添加到列表前面（最新的）
                    duration_data['日期'].insert(0, self.today_str)
                    duration_data['持续时间'].insert(0, today_result.duration)
                    
                    # 添加今天的物品数据
                    for item in today_result.items:
                        item_data['物品名称'].insert(0, item.name)
                        item_data['时间'].insert(0, item.timestamp)
                        item_data['日期'].insert(0, item.date)
                        item_data['归属配置组'].insert(0, item.config_group or '')

        # 更新实例变量
        self.duration_datadict = duration_data
        self.item_datadict = item_data
        
        # 获取有数据的日期列表
        filtered_logs = duration_data['日期']
        self.log_list = filtered_logs
        
        return filtered_logs

    def get_duration_data(self) -> Dict:
        """
        获取持续时间数据
        
        Returns:
            Dict: 持续时间数据字典
        """
        if not self.log_list:
            self.get_log_list()
        return self.duration_datadict

    def get_item_data(self) -> Dict:
        """
        获取物品数据
        
        Returns:
            Dict: 物品数据字典
        """
        if not self.log_list:
            self.get_log_list()
        return self.item_datadict
