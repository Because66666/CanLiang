#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试脚本 - 测试StreamController优化后的性能表现
"""

import time
import gc
import psutil
import os
from app.api.controllers import StreamController

def test_desktop_capture_performance():
    """测试桌面捕获性能"""
    print("=== 桌面捕获性能测试 ===")
    
    # 初始化StreamController
    sc = StreamController()
    
    # 预热
    print("预热中...")
    for _ in range(5):
        frame = sc._capture_desktop_optimized()
    
    # 性能测试
    test_frames = 20  # 减少测试帧数以降低内存使用
    print(f"开始捕获 {test_frames} 帧...")
    
    # 记录初始内存使用
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    start_time = time.time()
    
    for i in range(test_frames):
        frame = sc._capture_desktop_optimized()
        # 不存储帧数据，只测试捕获性能
        if (i + 1) % 5 == 0:
            print(f"已捕获 {i + 1} 帧")
    
    end_time = time.time()
    
    # 计算性能指标
    elapsed_time = end_time - start_time
    fps = test_frames / elapsed_time
    
    # 记录最终内存使用
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    print(f"\n性能测试结果:")
    print(f"总耗时: {elapsed_time:.2f} 秒")
    print(f"平均帧率: {fps:.1f} FPS")
    print(f"单帧平均耗时: {elapsed_time/test_frames*1000:.1f} ms")
    print(f"初始内存: {initial_memory:.1f} MB")
    print(f"最终内存: {final_memory:.1f} MB")
    print(f"内存增长: {memory_increase:.1f} MB")
    
    # 获取一帧用于显示尺寸信息
    sample_frame = sc._capture_desktop_optimized()
    if sample_frame is not None:
        print(f"帧尺寸: {sample_frame.shape}")
    
    # 清理资源
    sc._cleanup_resources()
    gc.collect()
    
    return fps, memory_increase

def test_window_capture_performance():
    """测试窗口捕获性能"""
    print("\n=== 窗口捕获性能测试 ===")
    
    sc = StreamController()
    
    # 获取可用程序
    programs = sc.get_available_programs()
    if not programs:
        print("未找到可用程序")
        return 0, 0
    
    # 选择第一个程序进行测试
    target_program = programs[0]
    print(f"测试程序: {target_program}")
    
    hwnd = sc.find_window_by_process_name(target_program)
    if hwnd == 0:
        print("未找到窗口句柄，使用桌面捕获")
        return test_desktop_capture_performance()
    
    # 预热
    print("预热中...")
    for _ in range(5):
        frame = sc._capture_normal_window_optimized(hwnd)
    
    # 性能测试
    test_frames = 20  # 减少测试帧数以降低内存使用
    print(f"开始捕获 {test_frames} 帧...")
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024
    
    start_time = time.time()
    
    for i in range(test_frames):
        frame = sc._capture_normal_window_optimized(hwnd)
        # 不存储帧数据，只测试捕获性能
        if (i + 1) % 5 == 0:
            print(f"已捕获 {i + 1} 帧")
    
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    fps = test_frames / elapsed_time
    
    final_memory = process.memory_info().rss / 1024 / 1024
    memory_increase = final_memory - initial_memory
    
    print(f"\n窗口捕获性能测试结果:")
    print(f"总耗时: {elapsed_time:.2f} 秒")
    print(f"平均帧率: {fps:.1f} FPS")
    print(f"单帧平均耗时: {elapsed_time/test_frames*1000:.1f} ms")
    print(f"内存增长: {memory_increase:.1f} MB")
    
    if frames:
        print(f"帧尺寸: {frames[0].shape}")
    
    sc._cleanup_resources()
    del frames
    gc.collect()
    
    return fps, memory_increase

def test_encoding_performance():
    """测试编码性能"""
    print("\n=== 编码性能测试 ===")
    
    sc = StreamController()
    
    # 捕获一帧用于编码测试
    frame = sc._capture_desktop_optimized()
    if frame is None:
        print("无法捕获帧进行编码测试")
        return
    
    print(f"测试帧尺寸: {frame.shape}")
    
    # 测试编码性能
    test_count = 20
    print(f"开始编码 {test_count} 次...")
    
    start_time = time.time()
    encoded_sizes = []
    
    for i in range(test_count):
        if sc._gpu_available:
            encoded_data = sc._encode_frame_gpu(frame)
        else:
            # 使用CPU编码
            import cv2
            _, encoded_data = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            encoded_data = encoded_data.tobytes()
        
        encoded_sizes.append(len(encoded_data))
        
        if (i + 1) % 5 == 0:
            print(f"已编码 {i + 1} 次")
    
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    encoding_fps = test_count / elapsed_time
    avg_size = sum(encoded_sizes) / len(encoded_sizes)
    
    print(f"\n编码性能测试结果:")
    print(f"编码方式: {'GPU' if sc._gpu_available else 'CPU'}")
    print(f"总耗时: {elapsed_time:.2f} 秒")
    print(f"编码帧率: {encoding_fps:.1f} FPS")
    print(f"单次编码耗时: {elapsed_time/test_count*1000:.1f} ms")
    print(f"平均编码大小: {avg_size/1024:.1f} KB")
    
    sc._cleanup_resources()

def main():
    """主测试函数"""
    print("StreamController 性能测试")
    print("=" * 50)
    
    try:
        # 测试桌面捕获性能
        desktop_fps, desktop_memory = test_desktop_capture_performance()
        
        # 测试窗口捕获性能
        window_fps, window_memory = test_window_capture_performance()
        
        # 测试编码性能
        test_encoding_performance()
        
        # 总结
        print("\n" + "=" * 50)
        print("性能测试总结:")
        print(f"桌面捕获帧率: {desktop_fps:.1f} FPS")
        print(f"窗口捕获帧率: {window_fps:.1f} FPS")
        print(f"桌面捕获内存增长: {desktop_memory:.1f} MB")
        print(f"窗口捕获内存增长: {window_memory:.1f} MB")
        
        # 性能评估
        if desktop_fps >= 25:
            print("✅ 桌面捕获性能优秀 (≥25 FPS)")
        elif desktop_fps >= 20:
            print("⚠️  桌面捕获性能良好 (≥20 FPS)")
        else:
            print("❌ 桌面捕获性能需要改进 (<20 FPS)")
        
        if desktop_memory < 50:
            print("✅ 内存使用优化良好 (<50 MB)")
        elif desktop_memory < 100:
            print("⚠️  内存使用可接受 (<100 MB)")
        else:
            print("❌ 内存使用过高 (≥100 MB)")
            
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()