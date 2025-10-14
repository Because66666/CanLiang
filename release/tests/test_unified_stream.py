#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一StreamController管理器测试脚本
测试优化后的StreamController管理方案的功能性和性能
"""

import sys
import os
import time
import psutil
import gc

# 添加项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.api.views import stream_manager

def test_singleton_pattern():
    """
    测试单例模式是否正常工作
    """
    print("=" * 50)
    print("测试1: 单例模式验证")
    print("=" * 50)
    
    # 获取两个管理器实例
    manager1 = stream_manager
    from app.api.views import StreamControllerManager
    manager2 = StreamControllerManager()
    
    # 验证是否为同一个实例
    is_singleton = manager1 is manager2
    print(f"单例模式验证: {'通过' if is_singleton else '失败'}")
    print(f"manager1 id: {id(manager1)}")
    print(f"manager2 id: {id(manager2)}")
    
    return is_singleton

def test_controller_reuse():
    """
    测试控制器实例复用功能
    """
    print("\n" + "=" * 50)
    print("测试2: 控制器实例复用")
    print("=" * 50)
    
    # 获取同一个target_app的控制器两次
    controller1 = stream_manager.get_controller("yuanshen.exe")
    controller2 = stream_manager.get_controller("yuanshen.exe")
    
    # 验证是否为同一个实例
    is_reused = controller1 is controller2
    print(f"实例复用验证: {'通过' if is_reused else '失败'}")
    print(f"controller1 id: {id(controller1)}")
    print(f"controller2 id: {id(controller2)}")
    print(f"target_app: {controller1.target_app}")
    
    # 获取不同target_app的控制器
    controller3 = stream_manager.get_controller("bettergi.exe")
    is_different = controller1 is not controller3
    print(f"不同应用实例分离: {'通过' if is_different else '失败'}")
    print(f"controller3 id: {id(controller3)}")
    print(f"controller3 target_app: {controller3.target_app}")
    
    return is_reused and is_different

def test_programs_list():
    """
    测试程序列表获取功能
    """
    print("\n" + "=" * 50)
    print("测试3: 程序列表获取")
    print("=" * 50)
    
    try:
        programs = stream_manager.get_programs_list()
        print(f"获取到程序列表: {programs}")
        print(f"程序数量: {len(programs)}")
        
        # 验证是否包含预期的程序
        expected_programs = ['yuanshen.exe', 'bettergi.exe', '桌面.exe']
        has_expected = all(prog in programs for prog in expected_programs)
        print(f"包含预期程序: {'通过' if has_expected else '失败'}")
        
        return len(programs) > 0 and has_expected
    except Exception as e:
        print(f"获取程序列表失败: {e}")
        return False

def test_memory_usage():
    """
    测试内存使用情况
    """
    print("\n" + "=" * 50)
    print("测试4: 内存使用优化")
    print("=" * 50)
    
    # 记录初始内存
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    print(f"初始内存使用: {initial_memory:.2f} MB")
    
    # 创建多个控制器实例（应该复用）
    controllers = []
    for i in range(10):
        controller = stream_manager.get_controller("yuanshen.exe")
        controllers.append(controller)
    
    # 记录创建后内存
    after_creation_memory = process.memory_info().rss / 1024 / 1024  # MB
    print(f"创建10个控制器后内存: {after_creation_memory:.2f} MB")
    
    # 验证所有控制器都是同一个实例
    all_same = all(c is controllers[0] for c in controllers)
    print(f"所有控制器实例相同: {'通过' if all_same else '失败'}")
    
    # 清理
    del controllers
    gc.collect()
    
    # 记录清理后内存
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    print(f"清理后内存使用: {final_memory:.2f} MB")
    
    memory_increase = after_creation_memory - initial_memory
    print(f"内存增长: {memory_increase:.2f} MB")
    
    # 内存增长应该很小（因为实例复用）
    memory_efficient = memory_increase < 50  # 小于50MB认为是高效的
    print(f"内存使用高效: {'通过' if memory_efficient else '失败'}")
    
    return all_same and memory_efficient

def test_cleanup_functionality():
    """
    测试清理功能
    """
    print("\n" + "=" * 50)
    print("测试5: 清理功能")
    print("=" * 50)
    
    # 创建几个控制器
    controller1 = stream_manager.get_controller("yuanshen.exe")
    controller2 = stream_manager.get_controller("bettergi.exe")
    
    print(f"创建前控制器数量: {len(stream_manager._controllers)}")
    
    # 停止特定控制器
    stream_manager.stop_controller("yuanshen.exe")
    print(f"停止yuanshen.exe后控制器数量: {len(stream_manager._controllers)}")
    
    # 清理所有控制器
    stream_manager.cleanup_all()
    print(f"清理所有后控制器数量: {len(stream_manager._controllers)}")
    
    cleanup_success = len(stream_manager._controllers) == 0
    print(f"清理功能: {'通过' if cleanup_success else '失败'}")
    
    return cleanup_success

def main():
    """
    主测试函数
    """
    print("开始测试统一StreamController管理器...")
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行所有测试
    test_results = []
    
    test_results.append(("单例模式", test_singleton_pattern()))
    test_results.append(("控制器复用", test_controller_reuse()))
    test_results.append(("程序列表", test_programs_list()))
    test_results.append(("内存优化", test_memory_usage()))
    test_results.append(("清理功能", test_cleanup_functionality()))
    
    # 输出测试结果汇总
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "通过" if result else "失败"
        print(f"{test_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\n总体结果: {passed_tests}/{total_tests} 测试通过")
    
    if passed_tests == total_tests:
        print("✅ 所有测试通过！StreamController管理器优化成功！")
    else:
        print("❌ 部分测试失败，需要进一步优化")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)