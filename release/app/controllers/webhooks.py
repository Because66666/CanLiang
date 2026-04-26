import logging
from typing import Dict, Any

from app.infrastructure.adapters import InquiryStoreAdapter, LegacyInquiryStoreAdapter

logger = logging.getLogger(__name__)


def validate_webhook_payload(payload: Dict[str, Any]) -> tuple[bool, str]:
    if 'event' not in payload:
        return False, '缺少必需的event字段'
    return True, ''


class WebhookController:
    """Webhook控制器：负责请求校验与数据库持久化协调。"""

    def __init__(self, log_dir: str, adapter: InquiryStoreAdapter | None = None):
        self.adapter = adapter or LegacyInquiryStoreAdapter(log_dir)

    def save_data(self, dict_list: Dict) -> Dict[str, Any]:
        try:
            valid, message = validate_webhook_payload(dict_list)
            if not valid:
                return {'success': False, 'message': message}

            success = self.adapter.save(dict_list)
            return {
                'success': bool(success),
                'message': '数据保存成功' if success else '数据保存失败'
            }
        except Exception as e:
            logger.error(f"保存webhook数据时发生错误: {e}")
            return {'success': False, 'message': f'服务器内部错误: {str(e)}'}

    def get_webhook_data(self, limit: int = 100) -> Dict[str, Any]:
        try:
            data_list = self.adapter.get_recent(limit)
            return {'success': True, 'data': data_list, 'count': len(data_list)}
        except Exception as e:
            logger.error(f"获取webhook数据时发生错误: {e}")
            return {
                'success': False,
                'message': f'获取数据失败: {str(e)}',
                'data': [],
                'count': 0
            }
