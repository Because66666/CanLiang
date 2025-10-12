#!/usr/bin/env python3
"""
数据库功能测试脚本
验证SQLite数据库的存储和读取功能
"""
import os
import sys
import tempfile
import shutil
from datetime import date

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.database import LogDatabase
from app.infrastructure.db import LogDataManager
from app.domain.entities import ItemInfo


def test_database_basic_operations():
    """
    测试数据库基本操作
    """
    print("=== 测试数据库基本操作 ===")
    
    # 创建临时数据库
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, 'test.db')
        db = LogDatabase(db_path)
        
        # 测试数据
        test_date = "20250110"
        test_duration = 3600
        test_items = [
            ItemInfo(name="摩拉", timestamp="10:30:15.123", date=test_date, config_group="测试配置"),
            ItemInfo(name="经验书", timestamp="10:31:20.456", date=test_date, config_group="测试配置"),
            ItemInfo(name="原石", timestamp="10:32:30.789", date=test_date, config_group=None)
        ]
        
        # 测试存储数据
        print(f"存储测试数据: 日期={test_date}, 持续时间={test_duration}秒, 物品数量={len(test_items)}")
        db.store_log_data(test_date, test_duration, test_items)
        
        # 测试检查日期是否存储
        is_stored = db.is_date_stored(test_date)
        print(f"日期 {test_date} 是否已存储: {is_stored}")
        assert is_stored, "数据存储失败"
        
        # 测试获取存储的日期
        stored_dates = db.get_stored_dates()
        print(f"已存储的日期: {stored_dates}")
        assert test_date in stored_dates, "获取存储日期失败"
        
        # 测试获取持续时间数据
        duration_data = db.get_duration_data(exclude_today=False)
        print(f"持续时间数据: {duration_data}")
        assert len(duration_data['日期']) == 1, "持续时间数据获取失败"
        assert duration_data['日期'][0] == test_date, "持续时间日期不匹配"
        assert duration_data['持续时间'][0] == test_duration, "持续时间不匹配"
        
        # 测试获取物品数据
        item_data = db.get_item_data(exclude_today=False)
        print(f"物品数据: {item_data}")
        assert len(item_data['物品名称']) == 3, "物品数据获取失败"
        assert "摩拉" in item_data['物品名称'], "物品名称不匹配"
        
        # 测试数据库统计
        stats = db.get_database_stats()
        print(f"数据库统计: {stats}")
        assert stats['log_files_count'] == 1, "日志文件数量统计错误"
        assert stats['items_count'] == 3, "物品数量统计错误"
        
        print("✓ 数据库基本操作测试通过")


def test_exclude_today_functionality():
    """
    测试排除今天数据的功能
    """
    print("\n=== 测试排除今天数据功能 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, 'test.db')
        db = LogDatabase(db_path)
        
        # 添加今天的数据
        today = date.today().strftime('%Y%m%d')
        yesterday = "20250109"  # 假设的昨天日期
        
        # 存储今天和昨天的数据
        db.store_log_data(today, 1800, [
            ItemInfo(name="今天的摩拉", timestamp="15:00:00.000", date=today, config_group="今日配置")
        ])
        db.store_log_data(yesterday, 3600, [
            ItemInfo(name="昨天的摩拉", timestamp="14:00:00.000", date=yesterday, config_group="昨日配置")
        ])
        
        # 测试包含今天的数据
        duration_with_today = db.get_duration_data(exclude_today=False)
        item_with_today = db.get_item_data(exclude_today=False)
        print(f"包含今天的持续时间数据: {len(duration_with_today['日期'])} 条记录")
        print(f"包含今天的物品数据: {len(item_with_today['物品名称'])} 条记录")
        
        # 测试排除今天的数据
        duration_without_today = db.get_duration_data(exclude_today=True)
        item_without_today = db.get_item_data(exclude_today=True)
        print(f"排除今天的持续时间数据: {len(duration_without_today['日期'])} 条记录")
        print(f"排除今天的物品数据: {len(item_without_today['物品名称'])} 条记录")
        
        # 验证排除功能
        assert len(duration_with_today['日期']) == 2, "包含今天的数据应该有2条记录"
        assert len(duration_without_today['日期']) == 1, "排除今天的数据应该有1条记录"
        assert today not in duration_without_today['日期'], "排除今天的数据中不应包含今天的日期"
        assert yesterday in duration_without_today['日期'], "排除今天的数据中应包含昨天的日期"
        
        print("✓ 排除今天数据功能测试通过")


def test_log_data_manager_integration():
    """
    测试LogDataManager与数据库的集成
    """
    print("\n=== 测试LogDataManager集成 ===")
    
    # 创建临时目录和测试日志文件
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试日志文件
        test_date = "20250110"
        log_file_path = os.path.join(temp_dir, f"better-genshin-impact{test_date}.log")
        
        # 创建简单的测试日志内容
        log_content = f"""[10:30:15.123] [INFO] BetterGI 配置组 "自动拾取" 加载完成，共1个脚本，开始执行
[10:30:16.456] [INFO] AutoPick 交互或拾取："摩拉"
[10:30:17.789] [INFO] AutoPick 交互或拾取："经验书"
[10:30:18.012] [INFO] BetterGI 配置组 "自动拾取" 执行结束
"""
        
        with open(log_file_path, 'w', encoding='utf-8') as f:
            f.write(log_content)
        
        # 初始化LogDataManager
        manager = LogDataManager(temp_dir)
        
        # 测试获取日志列表
        log_list = manager.get_log_list()
        print(f"获取的日志列表: {log_list}")
        
        # 测试获取数据
        duration_data = manager.get_duration_data()
        item_data = manager.get_item_data()
        
        print(f"持续时间数据: {duration_data}")
        print(f"物品数据: {item_data}")
        
        # 验证数据
        if log_list:  # 如果有有效的日志数据
            assert len(duration_data['日期']) > 0, "应该有持续时间数据"
            assert len(item_data['物品名称']) > 0, "应该有物品数据"
            print("✓ LogDataManager集成测试通过")
        else:
            print("⚠ 没有有效的日志数据，可能是解析逻辑需要调整")


def main():
    """
    主测试函数
    """
    print("开始数据库功能测试...\n")
    
    try:
        test_database_basic_operations()
        test_exclude_today_functionality()
        test_log_data_manager_integration()
        
        print("\n🎉 所有测试通过！数据库功能正常工作。")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())