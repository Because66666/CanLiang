"""
推流控制器性能与可用性验证测试

说明：
- 这些测试不依赖真实 Windows 图形栈，使用替身对象验证“可正常使用”与“基础性能”。
- 目标是给出稳定、可重复的验证信号，而不是做硬件基准测试。
"""

from __future__ import annotations

import sys
import time
import types

import numpy as np

from app.streaming.streamer import StreamController


class _FakeFinder:
    def __init__(self, hwnd: int = 0, programs: list[str] | None = None):
        self._hwnd = hwnd
        self._programs = programs or ['yuanshen.exe', 'bettergi.exe']

    def find(self, process_name: str) -> int:
        return self._hwnd

    def list_programs(self) -> list[str]:
        return list(self._programs)


class _FakeCapture:
    def __init__(self, shape: tuple[int, int, int] = (240, 320, 3)):
        self.shape = shape
        self.calls = 0

    def capture(self, hwnd: int, target_app: str = '') -> np.ndarray:
        self.calls += 1
        return np.zeros(self.shape, dtype=np.uint8)


def _install_stub_modules():
    cv2_stub = types.ModuleType('cv2')
    cv2_stub.IMWRITE_JPEG_QUALITY = 1
    cv2_stub.imencode = lambda _ext, _frame, _args: (True, np.array([1, 2, 3], dtype=np.uint8))
    sys.modules['cv2'] = cv2_stub

    win32gui_stub = types.ModuleType('win32gui')
    win32gui_stub.GetDesktopWindow = lambda: 999
    win32gui_stub.IsWindow = lambda _hwnd: True
    win32gui_stub.IsWindowVisible = lambda _hwnd: True
    sys.modules['win32gui'] = win32gui_stub


def test_stream_controller_basic_usage():
    """验证控制器可正常创建、查询程序列表、启动推流。"""
    _install_stub_modules()
    controller = StreamController(
        target_app='yuanshen.exe',
        finder=_FakeFinder(hwnd=123),
        capture=_FakeCapture(),
    )

    programs = controller.get_available_programs()
    assert 'yuanshen.exe' in programs

    gen = controller.generate_frames()
    frame_chunk = next(gen)
    assert b'Content-Type: image/jpeg' in frame_chunk
    controller.stop_stream()


def test_stream_frame_generation_performance():
    """验证生成帧性能在可接受范围（基础回归门槛）。"""
    _install_stub_modules()
    controller = StreamController(
        target_app='yuanshen.exe',
        finder=_FakeFinder(hwnd=123),
        capture=_FakeCapture(),
    )

    gen = controller.generate_frames()
    start = time.perf_counter()
    produced = 0
    for _ in range(10):
        _ = next(gen)
        produced += 1
    elapsed = time.perf_counter() - start
    controller.stop_stream()

    fps = produced / elapsed
    # 保守门槛：只要高于 20 FPS 就认为未出现明显退化
    assert fps > 20, f'Unexpected low frame generation throughput: {fps:.2f} FPS'


def test_program_listing_performance():
    """验证程序列表读取不出现明显性能问题。"""
    controller = StreamController(
        finder=_FakeFinder(programs=['yuanshen.exe', 'bettergi.exe', '桌面.exe']),
        capture=_FakeCapture(),
    )

    start = time.perf_counter()
    for _ in range(2000):
        programs = controller.get_available_programs()
        assert len(programs) == 3
    elapsed = time.perf_counter() - start

    assert elapsed < 1.0, f'Program listing regression detected: {elapsed:.3f}s'

