"""
工具类模块
静态数据处理工具，包括find_bettergi_install_path和open_browser_after_start
"""
import os
import subprocess
import threading
import time
import logging
from typing import Optional

logger = logging.getLogger('BetterGI初始化')


def find_bettergi_install_path() -> Optional[str]:
    """
    检测BetterGI的安装路径

    Returns:
        Optional[str]: 如果找到，返回BetterGI的安装路径；否则返回None
    """
    logger.info("正在检测BetterGI安装路径...")

    if os.name == 'nt':  # Windows系统
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            for i in range(0, winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    try:
                        display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                        if "BetterGI" in display_name:
                            install_location, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                            winreg.CloseKey(subkey)
                            winreg.CloseKey(key)
                            return install_location
                    except (FileNotFoundError, OSError):
                        pass
                    finally:
                        winreg.CloseKey(subkey)
                except (FileNotFoundError, OSError, WindowsError):
                    continue
            winreg.CloseKey(key)
        except Exception as e:
            logger.error(f"检测BetterGI安装路径时出错: {e}")

    elif os.name == 'posix':  # Linux系统
        try:
            result = subprocess.run(['which', 'BetterGI'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.error(f"检测BetterGI安装路径时出错: {e}")

    return None


def open_browser_after_start(port: int = 3000):
    """
    在Flask应用启动后打开浏览器
    
    Args:
        port: 端口号，默认为3000
    """

    def target():
        # 等待一段时间，确保Flask服务器完全启动
        time.sleep(2)
        url = f'http://127.0.0.1:{port}'
        try:
            subprocess.run(['start', url], shell=True, check=True)
            logger.info(f"成功启动浏览器并导航到 {url}")
        except subprocess.CalledProcessError as e:
            logger.error(f"启动浏览器时出现错误: {e}")
        except Exception as e:
            logger.error(f"启动浏览器时出现错误: {e}")
            try:
                subprocess.run(['start', url], check=True)
            except Exception as e:
                logger.error(f"启动浏览器时出现错误: {e}")

    # 在新线程中执行浏览器打开操作，避免阻塞Flask应用的启动
    threading.Thread(target=target).start()


def parse_timestamp_to_seconds(timestamp: str) -> float:
    """
    将时间戳字符串直接转换为当日的总秒数
    
    Args:
        timestamp: 时间戳字符串，格式: "04:10:02.395"
        
    Returns:
        float: 当日的总秒数，如 14402.395
    """
    parts = timestamp.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds_parts = parts[2].split('.')
    seconds = int(seconds_parts[0])
    milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0

    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000


def check_dict_empty(dictionary: dict) -> bool:
    """
    提供一个方法，判断自定义的字典数据结构是否有误或者为空
    
    Args:
        dictionary: 要检查的字典，值应该是列表
        
    Returns:
        bool: True表示为空，False表示不为空
        
    Raises:
        Exception: 当字典数据结构有误时抛出异常
    """
    lengths = {len(lst) for lst in dictionary.values()}
    if len(lengths) > 1:
        # 说明长度不一致
        raise Exception(f"字典数据结构有误，请检查数据结构。对应的长度有{lengths}")
    if lengths == {0}:
        return True
    else:
        return False