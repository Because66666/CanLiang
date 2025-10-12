"""
业务实体模块
定义Video、TextInfo等业务对象
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class LogEntry:
    """
    日志条目实体类
    
    Attributes:
        timestamp: 时间戳
        level: 日志级别
        log_type: 日志类型
        details: 日志详细内容
        date_str: 日期字符串
    """
    timestamp: str
    level: str
    log_type: str
    details: str
    date_str: str


@dataclass
class ItemInfo:
    """
    物品信息实体类
    
    Attributes:
        name: 物品名称
        timestamp: 拾取时间
        date: 拾取日期
        config_group: 归属配置组
    """
    name: str
    timestamp: str
    date: str
    config_group: Optional[str] = None


@dataclass
class DurationInfo:
    """
    持续时间信息实体类
    
    Attributes:
        date: 日期
        duration: 持续时间（秒）
    """
    date: str
    duration: int
    
    def format_duration(self) -> str:
        """
        将秒数转换为中文 x小时y分钟 格式
        
        Returns:
            str: 格式化后的时间字符串，如 "5小时30分钟"
        """
        if self.duration is None or self.duration == 0:
            return "0分钟"

        # 计算小时和分钟
        hours, remainder = divmod(int(self.duration), 3600)
        minutes, _ = divmod(remainder, 60)

        # 拼接字符串（忽略零值部分）
        parts = []
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0:
            parts.append(f"{minutes}分钟")

        return ''.join(parts) if parts else "0分钟"


@dataclass
class LogAnalysisResult:
    """
    日志分析结果实体类
    
    Attributes:
        item_count: 物品统计字典
        duration: 持续时间（秒）
        items: 物品信息列表
    """
    item_count: Dict[str, int]
    duration: int
    items: List[ItemInfo]


@dataclass
class ConfigGroup:
    """
    配置组实体类
    
    Attributes:
        name: 配置组名称
        script_count: 脚本数量
        start_time: 开始时间
        end_time: 结束时间
    """
    name: str
    script_count: int = 0
    start_time: Optional[str] = None
    end_time: Optional[str] = None