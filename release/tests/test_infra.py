"""
基础设施层测试模块
测试数据访问和工具类功能
"""
import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
from app.infrastructure.db import LogDataManager
from app.infrastructure.utils import (
    parse_timestamp_to_seconds, 
    check_dict_empty,
    find_bettergi_install_path
)


class TestUtils(unittest.TestCase):
    """
    工具类测试
    """
    
    def test_parse_timestamp_to_seconds(self):
        """
        测试时间戳解析功能
        """
        # 测试正常时间戳
        result = parse_timestamp_to_seconds("04:10:02.395")
        expected = 4 * 3600 + 10 * 60 + 2 + 0.395
        self.assertAlmostEqual(result, expected, places=3)
        
        # 测试没有毫秒的时间戳
        result = parse_timestamp_to_seconds("12:30:45")
        expected = 12 * 3600 + 30 * 60 + 45
        self.assertEqual(result, expected)
    
    def test_check_dict_empty(self):
        """
        测试字典空值检查功能
        """
        # 测试空字典
        empty_dict = {'a': [], 'b': [], 'c': []}
        self.assertTrue(check_dict_empty(empty_dict))
        
        # 测试非空字典
        non_empty_dict = {'a': [1, 2], 'b': [3, 4], 'c': [5, 6]}
        self.assertFalse(check_dict_empty(non_empty_dict))
        
        # 测试长度不一致的字典
        inconsistent_dict = {'a': [1, 2], 'b': [3], 'c': [4, 5, 6]}
        with self.assertRaises(Exception):
            check_dict_empty(inconsistent_dict)
    
    @patch('winreg.OpenKey')
    @patch('winreg.QueryInfoKey')
    @patch('winreg.EnumKey')
    @patch('winreg.QueryValueEx')
    def test_find_bettergi_install_path_windows(self, mock_query_value, mock_enum_key, 
                                               mock_query_info, mock_open_key):
        """
        测试Windows系统下BetterGI路径查找
        """
        # 模拟注册表操作
        mock_query_info.return_value = [1, None, None, None, None, None, None, None, None, None, None]
        mock_enum_key.return_value = "BetterGI_subkey"
        mock_query_value.side_effect = [
            ("BetterGI Application", None),  # DisplayName
            ("C:\\Program Files\\BetterGI", None)  # InstallLocation
        ]
        
        with patch('os.name', 'nt'):
            result = find_bettergi_install_path()
            self.assertEqual(result, "C:\\Program Files\\BetterGI")


class TestLogDataManager(unittest.TestCase):
    """
    日志数据管理器测试
    """
    
    def setUp(self):
        """
        测试前的设置
        """
        self.temp_dir = tempfile.mkdtemp()
        self.log_manager = LogDataManager(self.temp_dir)
    
    def tearDown(self):
        """
        测试后的清理
        """
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_parse_log(self):
        """
        测试日志解析功能
        """
        log_content = '''[12:00:00.000] [INFO] [TestClass] 配置组 "测试组" 加载完成，共1个脚本，开始执行
[12:01:00.000] [INFO] [TestClass] 交互或拾取："测试物品"
[12:02:00.000] [INFO] [TestClass] 配置组 "测试组" 执行结束'''
        
        result = self.log_manager.parse_log(log_content, "20250101")
        
        self.assertIsNotNone(result)
        self.assertIn("测试物品", result.item_count)
        self.assertEqual(result.item_count["测试物品"], 1)
        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0].name, "测试物品")
        self.assertEqual(result.items[0].config_group, "测试组")
    
    def test_read_log_file_not_found(self):
        """
        测试读取不存在的日志文件
        """
        result = self.log_manager.read_log_file("nonexistent.log", "20250101")
        self.assertIsNone(result)
    
    def test_get_log_list_empty_directory(self):
        """
        测试空目录的日志列表获取
        """
        result = self.log_manager.get_log_list()
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()