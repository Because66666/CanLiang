import logging
import ctypes

import cv2
import numpy as np
import win32api
import win32con
import win32gui
import win32ui

logger = logging.getLogger(__name__)


def apply_yuanshen_privacy_masks(img: np.ndarray, width: int, height: int) -> np.ndarray:
    base_width, base_height = 3840, 2160
    scale_x = width / base_width
    scale_y = height / base_height

    regions = [
        (222, 374, 583, 448),
        (3346, 2087, 3731, 2149),
    ]

    for x1, y1, x2, y2 in regions:
        rx1 = max(0, min(int(x1 * scale_x), width))
        ry1 = max(0, min(int(y1 * scale_y), height))
        rx2 = max(0, min(int(x2 * scale_x), width))
        ry2 = max(0, min(int(y2 * scale_y), height))
        if rx2 > rx1 and ry2 > ry1:
            cv2.rectangle(img, (rx1, ry1), (rx2, ry2), (0, 0, 0), -1)

    return img


class FrameCapture:
    """负责桌面与窗口截图。"""

    def capture(self, hwnd: int, target_app: str = '') -> np.ndarray:
        try:
            if hwnd == win32gui.GetDesktopWindow():
                return self._capture_desktop()
            return self._capture_normal_window(hwnd, target_app)
        except Exception as e:
            logger.error(f"捕获窗口时发生错误: {e}")
            return np.zeros((480, 640, 3), dtype=np.uint8)

    def _enable_dpi_awareness(self):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

    def _capture_desktop(self) -> np.ndarray:
        try:
            self._enable_dpi_awareness()
            screen_width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
            screen_left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
            screen_top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

            if screen_width == 0 or screen_height == 0:
                screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
                screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
                screen_left, screen_top = 0, 0

            desktop_dc = win32gui.GetDC(0)
            img_dc = win32ui.CreateDCFromHandle(desktop_dc)
            mem_dc = img_dc.CreateCompatibleDC()
            screenshot = win32ui.CreateBitmap()
            screenshot.CreateCompatibleBitmap(img_dc, screen_width, screen_height)
            mem_dc.SelectObject(screenshot)
            mem_dc.BitBlt((0, 0), (screen_width, screen_height), img_dc, (screen_left, screen_top), win32con.SRCCOPY)

            bmpstr = screenshot.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype='uint8')
            img.shape = (screen_height, screen_width, 4)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            mem_dc.DeleteDC()
            img_dc.DeleteDC()
            win32gui.ReleaseDC(0, desktop_dc)
            win32gui.DeleteObject(screenshot.GetHandle())
            return img
        except Exception as e:
            logger.error(f"捕获桌面时发生错误: {e}")
            return np.zeros((720, 1280, 3), dtype=np.uint8)

    def _capture_normal_window(self, hwnd: int, target_app: str) -> np.ndarray:
        try:
            if not hwnd or not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd):
                return np.zeros((480, 640, 3), dtype=np.uint8)

            self._enable_dpi_awareness()
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width, height = right - left, bottom - top
            if width <= 0 or height <= 0:
                return np.zeros((480, 640, 3), dtype=np.uint8)

            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            save_bitmap = win32ui.CreateBitmap()
            save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(save_bitmap)
            save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

            bmpstr = save_bitmap.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype='uint8')
            img.shape = (height, width, 4)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            if target_app == 'yuanshen.exe':
                img = apply_yuanshen_privacy_masks(img, width, height)

            win32gui.DeleteObject(save_bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)
            return img
        except Exception as e:
            logger.error(f"捕获普通窗口时发生错误: {e}")
            return np.zeros((480, 640, 3), dtype=np.uint8)
