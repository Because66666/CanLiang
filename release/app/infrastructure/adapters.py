"""
基础设施适配器
为控制器提供稳定的数据访问接缝，便于后续替换底层数据源实现。
"""

from __future__ import annotations

import os
from typing import Any, Protocol

from app.infrastructure.database import DatabaseManager


class InquiryStoreAdapter(Protocol):
    """查询/写入适配器接口。"""

    def get_by_id(self, record_id: int) -> dict[str, Any] | None:
        ...

    def get_recent(self, limit: int = 100) -> list[dict[str, Any]]:
        ...

    def save(self, payload: dict[str, Any]) -> bool:
        ...


class LegacyInquiryStoreAdapter:
    """
    旧数据路径适配器。
    默认仍通过 DatabaseManager 访问原有 SQLite 实现。
    """

    def __init__(self, log_dir: str, db_manager: DatabaseManager | None = None):
        db_path = os.path.join(log_dir, 'CanLiangData.db')
        self.db_manager = db_manager or DatabaseManager(db_path)

    def get_by_id(self, record_id: int) -> dict[str, Any] | None:
        records = self.get_recent(limit=1000)
        for record in records:
            if record.get('id') == record_id:
                return record
        return None

    def get_recent(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.db_manager.get_webhook_data(limit)

    def save(self, payload: dict[str, Any]) -> bool:
        return self.db_manager.save_webhook_data(payload)

