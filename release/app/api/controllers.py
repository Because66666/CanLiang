"""
控制器模块
封装接口的业务逻辑
"""
import logging
from typing import Dict, List, Any
from app.infrastructure.db import LogDataManager
from app.infrastructure.utils import check_dict_empty

logger = logging.getLogger('BetterGI初始化')


class LogController:
    """
    日志控制器
    处理日志相关的业务逻辑
    """
    
    def __init__(self, log_dir: str):
        """
        初始化日志控制器
        
        Args:
            log_dir: 日志目录路径
        """
        self.log_manager = LogDataManager(log_dir)
    
    def get_log_list(self) -> Dict[str, List[str]]:
        """
        获取日志文件列表
        
        Returns:
            Dict[str, List[str]]: 包含日志文件列表的字典，格式：{'list': ['20250501']}
        """
        try:
            if not self.log_manager.log_list:
                log_list = self.log_manager.get_log_list()
            else:
                log_list = self.log_manager.log_list
            
            # 最新的日志排在前面
            log_list.reverse()
            return {'list': log_list}
        except Exception as e:
            logger.error(f"获取日志列表时发生错误: {e}")
            return {'list': []}
    
    def get_log_data(self) -> Dict[str, Any]:
        """
        获取日志分析数据
        
        Returns:
            Dict[str, Any]: 包含持续时间和物品数据的字典，格式：{
                'duration': duration_dict,
                'item': item_dict
            }
        """
        try:
            # 检查数据是否为空，如果为空则重新加载
            duration_data = self.log_manager.get_duration_data()
            item_data = self.log_manager.get_item_data()
            
            if check_dict_empty(duration_data) or check_dict_empty(item_data):
                self.log_manager.get_log_list()
                duration_data = self.log_manager.get_duration_data()
                item_data = self.log_manager.get_item_data()
            
            return {
                'duration': duration_data,
                'item': item_data
            }
        except Exception as e:
            logger.error(f"获取日志数据时发生错误: {e}")
            return {
                'duration': {'日期': [], '持续时间': []},
                'item': {'物品名称': [], '时间': [], '日期': [], '归属配置组': []}
            }