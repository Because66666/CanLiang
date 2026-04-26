import logging
import time
from typing import Any, Dict, List

import numpy as np
from flask import Response

from app.streaming.capture import FrameCapture
from app.streaming.window_finder import WindowFinder

logger = logging.getLogger(__name__)


class StreamController:
    """推流控制器：负责推流状态机，窗口查找与画面捕获通过协作者完成。"""

    def __init__(self, target_app: str = 'yuanshen.exe', finder: WindowFinder | None = None,
                 capture: FrameCapture | None = None):
        self.target_app = target_app
        self.is_streaming = False
        self.hwnd = None
        self.finder = finder or WindowFinder()
        self.capture = capture or FrameCapture()

    def find_window_by_process_name(self, process_name: str) -> int:
        return self.finder.find(process_name)

    def capture_window(self, hwnd: int) -> np.ndarray:
        return self.capture.capture(hwnd, self.target_app)

    def generate_frames(self):
        try:
            import cv2
            import win32gui

            if self.target_app == '桌面.exe':
                self.hwnd = win32gui.GetDesktopWindow()
            else:
                self.hwnd = self.find_window_by_process_name(self.target_app)

            if not self.hwnd:
                logger.warning(f"未找到进程 {self.target_app} 的窗口")
                self.is_streaming = True
                while self.is_streaming:
                    try:
                        frame = np.zeros((480, 640, 3), dtype=np.uint8)
                        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                        if ret:
                            frame_bytes = buffer.tobytes()
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                        time.sleep(1 / 30)
                    except GeneratorExit:
                        logger.info(f"检测到客户端断开连接，停止推流 - 目标应用: {self.target_app}")
                        self.is_streaming = False
                        break
                    except Exception as e:
                        logger.error(f"生成黑屏帧时发生错误: {e}")
                        time.sleep(0.1)
                return

            self.is_streaming = True
            logger.info(f"开始推流 - 目标应用: {self.target_app}")

            while self.is_streaming:
                try:
                    if self.target_app != '桌面.exe':
                        if not win32gui.IsWindow(self.hwnd) or not win32gui.IsWindowVisible(self.hwnd):
                            logger.warning(f"窗口句柄 {self.hwnd} 已失效，重新查找窗口")
                            self.hwnd = self.find_window_by_process_name(self.target_app)
                            if not self.hwnd:
                                logger.warning(f"无法重新找到进程 {self.target_app} 的窗口，返回黑屏")
                                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                                self.is_streaming = False
                            else:
                                frame = self.capture_window(self.hwnd)
                        else:
                            frame = self.capture_window(self.hwnd)
                    else:
                        frame = self.capture_window(self.hwnd)

                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    if ret:
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

                    time.sleep(1 / 30)
                except GeneratorExit:
                    logger.info(f"检测到客户端断开连接，停止推流 - 目标应用: {self.target_app}")
                    self.is_streaming = False
                    break
                except Exception as e:
                    logger.error(f"生成视频帧时发生错误: {e}")
                    time.sleep(0.1)
        finally:
            if self.is_streaming:
                self.is_streaming = False
                logger.info(f"推流已停止 - 目标应用: {self.target_app}")

    def start_stream(self) -> Response:
        return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def stop_stream(self):
        self.is_streaming = False
        logger.info('视频流已停止')

    def get_stream_info(self) -> Dict[str, Any]:
        import win32gui

        return {
            'target_app': self.target_app,
            'is_streaming': self.is_streaming,
            'window_found': bool(self.hwnd and self.hwnd != win32gui.GetDesktopWindow()),
            'hwnd': self.hwnd,
        }

    def get_available_programs(self) -> List[str]:
        return self.finder.list_programs()
