"""
API层测试模块
测试API接口的功能
"""
import unittest
import json
from unittest.mock import patch, MagicMock
from app import create_app
from app.api.views import init_controllers


class TestAPI(unittest.TestCase):
    """
    API测试类
    """
    
    def setUp(self):
        """
        测试前的设置
        """
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # 模拟初始化控制器
        with patch('app.api.views.LogController') as mock_controller:
            init_controllers('/fake/log/dir')
    
    def test_serve_index(self):
        """
        测试首页路由
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.api.views.log_controller')
    def test_get_log_list_api(self, mock_controller):
        """
        测试获取日志列表API
        """
        # 模拟控制器返回数据
        mock_controller.get_log_list.return_value = {'list': ['20250101', '20250102']}
        
        response = self.client.get('/api/LogList')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('list', data)
        self.assertEqual(len(data['list']), 2)
    
    @patch('app.api.views.log_controller')
    def test_analyse_log(self, mock_controller):
        """
        测试日志分析API
        """
        # 模拟控制器返回数据
        mock_data = {
            'duration': {'日期': ['20250101'], '持续时间': [3600]},
            'item': {'物品名称': ['测试物品'], '时间': ['12:00:00'], '日期': ['20250101'], '归属配置组': ['测试组']}
        }
        mock_controller.get_log_data.return_value = mock_data
        
        response = self.client.get('/api/LogData')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('duration', data)
        self.assertIn('item', data)
    
    def test_controller_not_initialized(self):
        """
        测试控制器未初始化的情况
        """
        # 重新创建应用但不初始化控制器
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        response = client.get('/api/LogList')
        self.assertEqual(response.status_code, 500)
        
        data = json.loads(response.data)
        self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()