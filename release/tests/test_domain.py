"""
领域层测试模块
测试业务实体和核心规则
"""
import unittest
from app.domain.entities import (
    LogEntry, ItemInfo, DurationInfo, 
    LogAnalysisResult, ConfigGroup
)


class TestEntities(unittest.TestCase):
    """
    实体类测试
    """
    
    def test_log_entry_creation(self):
        """
        测试日志条目实体创建
        """
        log_entry = LogEntry(
            timestamp="12:00:00.000",
            level="INFO",
            log_type="TestClass",
            details="测试日志内容",
            date_str="20250101"
        )
        
        self.assertEqual(log_entry.timestamp, "12:00:00.000")
        self.assertEqual(log_entry.level, "INFO")
        self.assertEqual(log_entry.log_type, "TestClass")
        self.assertEqual(log_entry.details, "测试日志内容")
        self.assertEqual(log_entry.date_str, "20250101")
    
    def test_item_info_creation(self):
        """
        测试物品信息实体创建
        """
        item_info = ItemInfo(
            name="测试物品",
            timestamp="12:00:00.000",
            date="20250101",
            config_group="测试组"
        )
        
        self.assertEqual(item_info.name, "测试物品")
        self.assertEqual(item_info.timestamp, "12:00:00.000")
        self.assertEqual(item_info.date, "20250101")
        self.assertEqual(item_info.config_group, "测试组")
    
    def test_item_info_optional_config_group(self):
        """
        测试物品信息实体的可选配置组
        """
        item_info = ItemInfo(
            name="测试物品",
            timestamp="12:00:00.000",
            date="20250101"
        )
        
        self.assertIsNone(item_info.config_group)
    
    def test_duration_info_format_duration(self):
        """
        测试持续时间格式化功能
        """
        # 测试0分钟
        duration_info = DurationInfo(date="20250101", duration=0)
        self.assertEqual(duration_info.format_duration(), "0分钟")
        
        # 测试只有分钟
        duration_info = DurationInfo(date="20250101", duration=1800)  # 30分钟
        self.assertEqual(duration_info.format_duration(), "30分钟")
        
        # 测试只有小时
        duration_info = DurationInfo(date="20250101", duration=7200)  # 2小时
        self.assertEqual(duration_info.format_duration(), "2小时")
        
        # 测试小时和分钟
        duration_info = DurationInfo(date="20250101", duration=5430)  # 1小时30分钟30秒
        self.assertEqual(duration_info.format_duration(), "1小时30分钟")
        
        # 测试None值
        duration_info = DurationInfo(date="20250101", duration=None)
        self.assertEqual(duration_info.format_duration(), "0分钟")
    
    def test_log_analysis_result_creation(self):
        """
        测试日志分析结果实体创建
        """
        items = [
            ItemInfo("物品1", "12:00:00", "20250101", "组1"),
            ItemInfo("物品2", "12:01:00", "20250101", "组2")
        ]
        
        result = LogAnalysisResult(
            item_count={"物品1": 1, "物品2": 1},
            duration=3600,
            items=items
        )
        
        self.assertEqual(len(result.items), 2)
        self.assertEqual(result.duration, 3600)
        self.assertEqual(result.item_count["物品1"], 1)
        self.assertEqual(result.item_count["物品2"], 1)
    
    def test_config_group_creation(self):
        """
        测试配置组实体创建
        """
        config_group = ConfigGroup(
            name="测试配置组",
            script_count=5,
            start_time="12:00:00",
            end_time="12:30:00"
        )
        
        self.assertEqual(config_group.name, "测试配置组")
        self.assertEqual(config_group.script_count, 5)
        self.assertEqual(config_group.start_time, "12:00:00")
        self.assertEqual(config_group.end_time, "12:30:00")
    
    def test_config_group_default_values(self):
        """
        测试配置组实体的默认值
        """
        config_group = ConfigGroup(name="测试配置组")
        
        self.assertEqual(config_group.name, "测试配置组")
        self.assertEqual(config_group.script_count, 0)
        self.assertIsNone(config_group.start_time)
        self.assertIsNone(config_group.end_time)


if __name__ == '__main__':
    unittest.main()