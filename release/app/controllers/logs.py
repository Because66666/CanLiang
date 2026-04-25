import logging
from typing import Dict, List, Any

from app.infrastructure.manager import LogDataManager

logger = logging.getLogger(__name__)


class LogController:
    """日志控制器：协调日志管理器并格式化返回数据。"""

    def __init__(self, log_dir: str):
        self.log_manager = LogDataManager(log_dir)

    def get_log_list(self) -> Dict[str, List[str]]:
        try:
            if not self.log_manager.log_list:
                log_list = self.log_manager.get_log_list()
            else:
                log_list = list(self.log_manager.log_list)

            return {'list': sorted(log_list, reverse=True)}
        except Exception as e:
            logger.error(f"获取日志列表时发生错误: {e}")
            return {'list': []}

    def get_log_data(self) -> Dict[str, Any]:
        try:
            self.log_manager.get_log_list()
            duration_data = self._build_duration_payload()
            item_data = self.log_manager.item_datadict
            return {'duration': duration_data, 'item': item_data}
        except Exception as e:
            logger.error(f"获取日志数据时发生错误: {e}")
            return {
                'duration': {'日期': [], '持续时间': []},
                'item': {'物品名称': [], '时间': [], '日期': [], '归属配置组': []}
            }

    def _build_duration_payload(self) -> Dict[str, List[Any]]:
        duration_cache = self.log_manager.duration_datadict
        if isinstance(duration_cache, dict) and '日期' not in duration_cache:
            sorted_dates = sorted(duration_cache.keys(), reverse=True)
            return {
                '日期': sorted_dates,
                '持续时间': [duration_cache[date_str] for date_str in sorted_dates]
            }

        return {'日期': [], '持续时间': []}
