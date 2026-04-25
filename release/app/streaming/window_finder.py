import logging
import os
from typing import Callable, List

logger = logging.getLogger(__name__)


class WindowFinder:
    """负责视窗列举与查找，供推流和程序列表共用。"""

    def _iter_visible_windows(self, handler: Callable[[int, int], None]):
        import win32gui
        import win32process

        def enum_windows_proc(hwnd, l_param):
            if not win32gui.IsWindowVisible(hwnd):
                return True
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                handler(hwnd, pid)
            except Exception as e:
                logger.debug(f"枚举窗口时发生错误: {e}")
            return True

        win32gui.EnumWindows(enum_windows_proc, None)

    def _resolve_process_name(self, pid: int) -> str | None:
        import win32api
        import win32con
        import win32process

        process_handle = None
        try:
            process_handle = win32api.OpenProcess(
                win32con.PROCESS_QUERY_LIMITED_INFORMATION,
                False,
                pid
            )
            process_path = win32process.GetModuleFileNameEx(process_handle, 0)
            return os.path.basename(process_path).lower()
        except Exception:
            try:
                process_handle = win32api.OpenProcess(
                    win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                    False,
                    pid
                )
                process_path = win32process.GetModuleFileNameEx(process_handle, 0)
                return os.path.basename(process_path).lower()
            except Exception:
                try:
                    import psutil
                    return psutil.Process(pid).name().lower()
                except Exception:
                    return None
        finally:
            if process_handle:
                try:
                    win32api.CloseHandle(process_handle)
                except Exception:
                    pass

    def find(self, process_name: str) -> int:
        windows: List[int] = []

        def handler(hwnd: int, pid: int):
            if windows:
                return
            current_name = self._resolve_process_name(pid)
            if current_name and current_name == process_name.lower():
                windows.append(hwnd)

        self._iter_visible_windows(handler)
        return windows[0] if windows else 0

    def list_programs(self) -> List[str]:
        import win32gui

        programs: List[str] = []

        def handler(hwnd: int, pid: int):
            window_title = win32gui.GetWindowText(hwnd)
            if not window_title.strip():
                return
            process_name = self._resolve_process_name(pid)
            if process_name and process_name not in ['system', 'dwm.exe', 'explorer.exe']:
                programs.append(process_name)

        self._iter_visible_windows(handler)
        unique_programs = sorted(list(set(programs)))
        logger.debug(f"扫描完成，找到 {len(unique_programs)} 个可推流程序")
        return unique_programs
