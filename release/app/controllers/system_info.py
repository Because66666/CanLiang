import logging
from typing import Dict, Protocol

import psutil

logger = logging.getLogger(__name__)


class SystemMetrics(Protocol):
    def memory_percent(self) -> float:
        ...

    def cpu_percent(self, interval: float) -> float:
        ...


class PsutilMetrics:
    def memory_percent(self) -> float:
        return psutil.virtual_memory().percent

    def cpu_percent(self, interval: float) -> float:
        return psutil.cpu_percent(interval=interval)


class SystemInfoController:
    """系统信息控制器：负责格式化系统资源使用率数据。"""

    def __init__(self, metrics: SystemMetrics | None = None):
        self.metrics = metrics or PsutilMetrics()

    def get_memory_usage(self) -> float:
        try:
            return round(self.metrics.memory_percent(), 1)
        except Exception as e:
            logger.error(f"获取内存使用率时发生错误: {e}")
            return 0.0

    def get_cpu_usage(self, interval: float = 1.0) -> float:
        try:
            return round(self.metrics.cpu_percent(interval), 1)
        except Exception as e:
            logger.error(f"获取CPU使用率时发生错误: {e}")
            return 0.0

    def get_system_info(self) -> Dict[str, float]:
        try:
            return {
                'memory_usage': self.get_memory_usage(),
                'cpu_usage': self.get_cpu_usage()
            }
        except Exception as e:
            logger.error(f"获取系统信息时发生错误: {e}")
            return {'memory_usage': 0.0, 'cpu_usage': 0.0}
