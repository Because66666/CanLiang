"""
控制器模块
封装接口的业务逻辑
"""
import logging
from typing import Dict, List, Any
from app.infrastructure.manager import LogDataManager
from app.infrastructure.database import DatabaseManager
from app.infrastructure.utils import check_dict_empty
import os

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
            
            # if check_dict_empty(duration_data) or check_dict_empty(item_data):
            #     self.log_manager.get_log_list()
            #     duration_data = self.log_manager.get_duration_data()
            #     item_data = self.log_manager.get_item_data()
            
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


class WebhookController:
    """
    Webhook控制器
    处理webhook相关的业务逻辑
    """
    
    def __init__(self, log_dir: str):
        """
        初始化webhook控制器
        
        Args:
            log_dir: 日志目录路径
        """
        # 初始化数据库管理器
        db_path = os.path.join(log_dir, 'CanLiangData.db')
        self.db_manager = DatabaseManager(db_path)
    
    def save_data(self, dict_list: Dict) -> Dict[str, Any]:
        """
        保存webhook数据
        
        Args:
            dict_list: 包含webhook数据的字典，必须包含'event'字段
            
        Returns:
            Dict[str, Any]: 操作结果，包含success状态和message信息
        """
        try:
            # 验证必需字段
            if 'event' not in dict_list:
                return {
                    'success': False,
                    'message': '缺少必需的event字段'
                }
            
            # 保存数据到数据库
            success = self.db_manager.save_webhook_data(dict_list)
            
            if success:
                return {
                    'success': True,
                    'message': '数据保存成功'
                }
            else:
                return {
                    'success': False,
                    'message': '数据保存失败'
                }
                
        except Exception as e:
            logger.error(f"保存webhook数据时发生错误: {e}")
            return {
                'success': False,
                'message': f'服务器内部错误: {str(e)}'
            }
    
    def get_webhook_data(self, limit: int = 100) -> Dict[str, Any]:
        """
        获取webhook数据列表
        
        Args:
            limit: 返回记录数限制
            
        Returns:
            Dict[str, Any]: 包含数据列表的字典
        """
        try:
            data_list = self.db_manager.get_webhook_data(limit)
            return {
                'success': True,
                'data': data_list,
                'count': len(data_list)
            }
        except Exception as e:
            logger.error(f"获取webhook数据时发生错误: {e}")
            return {
                'success': False,
                'message': f'获取数据失败: {str(e)}',
                'data': [],
                'count': 0
            }