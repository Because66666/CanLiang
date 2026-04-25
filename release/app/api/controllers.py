"""
控制器聚合模块（向后兼容）

说明：
- 该模块保留旧导入路径 `app.api.controllers`，避免影响现有调用方。
- 控制器实现已拆分到 `app.controllers` 与 `app.streaming` 子模块中。
"""

from app.controllers.logs import LogController
from app.controllers.webhooks import WebhookController
from app.controllers.system_info import SystemInfoController
from app.streaming.streamer import StreamController

__all__ = [
    'LogController',
    'WebhookController',
    'StreamController',
    'SystemInfoController',
]
