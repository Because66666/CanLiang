#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BetterGI日志分析工具初始化脚本

此脚本用于初始化BetterGI日志分析工具的运行环境，包括：
1. 检测BetterGI安装路径
2. 配置Python虚拟环境
3. 安装前端依赖
4. 启动后端和前端服务

脚本会检测是否首次运行，如果不是首次运行，将跳过环境配置步骤直接启动服务器。

作者: Because66666
版本: 1.1.0
"""

import os
import sys
import subprocess
import platform
import logging
import signal
import time
import json
from typing import Optional, Tuple, List, Dict, Any, Union

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('BetterGI初始化')

# 全局变量
script_dir = os.path.dirname(os.path.abspath(__file__))
server_processes = []

# 初始化标记文件路径
INIT_MARKER_FILE = os.path.join(script_dir, '.bettergi_init_completed')


def setup_signal_handlers() -> None:
    """
    设置信号处理器，确保程序能够正常退出
    """

    def signal_handler(sig, frame):
        logger.info("接收到终止信号，正在关闭服务...")
        cleanup_resources()
        logger.info("程序已退出。")
        sys.exit(0)

    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    if os.name == 'posix':  # 仅在类Unix系统上注册SIGTERM
        signal.signal(signal.SIGTERM, signal_handler)


def cleanup_resources() -> None:
    """
    清理资源，确保所有子进程被正确终止
    """
    for process in server_processes:
        if process and process.poll() is None:  # 检查进程是否仍在运行
            try:
                logger.info(f"正在终止进程 PID: {process.pid}")
                if os.name == 'nt':  # Windows
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:  # Unix/Linux
                    process.terminate()
                    process.wait(timeout=5)  # 等待进程终止，最多5秒
            except Exception as e:
                logger.error(f"终止进程时出错: {e}")


def find_bettergi_install_path() -> Optional[str]:
    """
    检测BetterGI的安装路径

    返回:
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


def setup_env_file(install_path: Optional[str]) -> None:
    """
    设置环境变量文件

    参数:
        install_path (Optional[str]): BetterGI的安装路径
    """
    env_file_path = os.path.join(script_dir, 'mini', '.env')
    os.makedirs(os.path.dirname(env_file_path), exist_ok=True)

    if install_path:
        logger.info(f"成功检测到BetterGI安装路径: {install_path}")
        with open(env_file_path, 'w', encoding='utf8') as f:
            f.write(f"#此处填写BetterGI的安装文件夹路径。\nBETTERGI_PATH={install_path}")
    else:
        logger.warning("未能检测到BetterGI安装路径。请手动在/mini/.env中填写安装BetterGI的路径")


def setup_python_env() -> bool:
    """
    设置Python虚拟环境并安装依赖

    返回:
        bool: 安装成功返回True，否则返回False
    """
    logger.info("准备安装Python环境...")

    # 定义项目根目录和虚拟环境目录
    project_root = os.path.join(script_dir, 'mini')
    venv_dir = os.path.join(project_root, '.venv')
    requirements_file = os.path.join(project_root, 'requirements.txt')

    # 检查requirements.txt是否存在
    if not os.path.exists(requirements_file):
        logger.error(f"依赖文件不存在: {requirements_file}")
        return False

    # 激活虚拟环境的命令（根据不同操作系统）
    if os.name == 'nt':
        activate_script = os.path.join(venv_dir, 'Scripts', 'activate.bat')
    else:
        activate_script = os.path.join(venv_dir, 'bin', 'activate')

    # 检查虚拟环境是否存在，如果不存在则创建
    if not os.path.exists(venv_dir):
        try:
            logger.info("创建Python虚拟环境...")
            subprocess.run(['python', '-m', 'venv', venv_dir], check=True)
            logger.info("虚拟环境创建成功。")
        except subprocess.CalledProcessError as e:
            logger.error(f"创建虚拟环境时出错: {e}")
            return False

    # 安装依赖
    try:
        logger.info("安装Python依赖...")
        if os.name == 'nt':
            install_command = f'call "{activate_script}" && pip install -r "{requirements_file}"'
            subprocess.run(install_command, shell=True, check=True)
        else:
            install_command = f'source "{activate_script}" && pip install -r "{requirements_file}"'
            subprocess.run(install_command, shell=True, executable='/bin/bash', check=True)
        logger.info("Python依赖安装成功。")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"安装Python依赖时出错: {e}")
        return False


def is_npm_installed() -> bool:
    """
    检查npm是否已安装

    返回:
        bool: 如果npm已安装返回True，否则返回False
    """
    try:
        command = 'npm --version'
        if os.name == 'nt':  # Windows系统
            result = subprocess.run(['cmd.exe', '/c', command],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    check=True)
        else:  # Linux或macOS等类Unix系统
            result = subprocess.run(command.split(),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    check=True)
        npm_version = result.stdout.decode('utf-8').strip()
        logger.info(f"检测到npm版本: {npm_version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("npm未安装")
        return False


def setup_frontend_env() -> bool:
    """
    设置前端环境，安装依赖并构建

    返回:
        bool: 安装成功返回True，否则返回False
    """
    logger.info("准备安装前端环境...")

    if not is_npm_installed():
        logger.error("npm未安装，请先安装npm。")
        return False

    working_dir = os.path.join(script_dir, 'website')
    if not os.path.exists(working_dir):
        logger.error(f"错误: 前端目录不存在: {working_dir}")
        return False

    try:
        logger.info("开始安装前端依赖...")
        if os.name == 'nt':  # Windows系统
            subprocess.run(['cmd.exe', '/c', 'npm install --force'], cwd=working_dir, check=True)
            logger.info("前端依赖安装成功，开始构建...")
            subprocess.run(['cmd.exe', '/c', 'npm run build'], cwd=working_dir, check=True)
        else:
            subprocess.run(['npm', 'install', '--force'], cwd=working_dir, check=True)
            logger.info("前端依赖安装成功，开始构建...")
            subprocess.run(['npm', 'run', 'build'], cwd=working_dir, check=True)
        logger.info("前端环境安装和构建成功。")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"前端环境安装失败: {e}")
        return False


def start_backend_server() -> Optional[subprocess.Popen]:
    """
    启动后端服务器

    返回:
        Optional[subprocess.Popen]: 如果成功启动，返回进程对象；否则返回None
    """
    logger.info("准备启动后端服务器...")

    system = platform.system()
    venv_dir = os.path.join(script_dir, 'mini', '.venv')
    app_path = os.path.join(script_dir, 'mini', 'app.py')

    if not os.path.exists(app_path):
        logger.error(f"后端应用文件不存在: {app_path}")
        return None

    server = None
    try:
        if system == "Windows":
            activate_script = os.path.join(venv_dir, 'Scripts', 'activate.bat')
            full_command = f'call "{activate_script}" && python "{app_path}"'
            server = subprocess.Popen(full_command, shell=True)
            logger.info(f"后端服务器已启动，PID: {server.pid}")
        elif system == "Linux" or system == "Darwin":  # Linux或macOS
            activate_script = os.path.join(venv_dir, 'bin', 'activate')
            full_command = f'source "{activate_script}" && python "{app_path}"'
            server = subprocess.Popen(full_command, shell=True, executable='/bin/bash')
            logger.info(f"后端服务器已启动，PID: {server.pid}")
        else:
            logger.error(f"不支持的操作系统: {system}")
            return None

        # 给服务器一些启动时间
        time.sleep(2)

        # 检查进程是否仍在运行
        if server.poll() is not None:
            logger.error(f"后端服务器启动失败，退出码: {server.returncode}")
            return None

        return server
    except Exception as e:
        logger.error(f"启动后端服务器时出错: {e}")
        return None


def start_frontend_server() -> Optional[subprocess.Popen]:
    """
    启动前端服务器

    返回:
        Optional[subprocess.Popen]: 如果成功启动，返回进程对象；否则返回None
    """
    logger.info("准备启动前端服务器...")

    system = platform.system()
    working_dir = os.path.join(script_dir, 'website')

    if not os.path.exists(working_dir):
        logger.error(f"前端目录不存在: {working_dir}")
        return None

    website = None
    try:
        if system == "Windows":
            website = subprocess.Popen(['cmd.exe', '/c', 'npm run start'],
                                       cwd=working_dir)
            logger.info(f"前端服务器已启动，PID: {website.pid}")
        elif system == "Linux" or system == "Darwin":  # Linux或macOS
            website = subprocess.Popen(['npm', 'run', 'start'],
                                       cwd=working_dir)
            logger.info(f"前端服务器已启动，PID: {website.pid}")
        else:
            logger.error(f"不支持的操作系统: {system}")
            return None

        # 给服务器一些启动时间
        time.sleep(2)

        # 检查进程是否仍在运行
        if website.poll() is not None:
            logger.error(f"前端服务器启动失败，退出码: {website.returncode}")
            return None

        return website
    except Exception as e:
        logger.error(f"启动前端服务器时出错: {e}")
        return None


def is_first_run() -> bool:
    """
    检查是否首次运行

    返回:
        bool: 如果是首次运行返回True，否则返回False
    """
    return not os.path.exists(INIT_MARKER_FILE)


def create_init_marker() -> None:
    """
    创建初始化完成标记文件
    """
    try:
        # 创建标记文件，记录初始化时间和环境信息
        marker_data = {
            "init_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system": platform.system(),
            "python_version": platform.python_version(),
        }

        with open(INIT_MARKER_FILE, 'w', encoding='utf-8') as f:
            json.dump(marker_data, f, ensure_ascii=False, indent=2)

        logger.info(f"已创建初始化标记文件: {INIT_MARKER_FILE}")
    except Exception as e:
        logger.warning(f"创建初始化标记文件失败: {e}")

def open_browser(url: str) -> None:
    """
    打开默认浏览器并导航到指定URL

    参数:
        url (str): 要导航到的URL
    """
    import webbrowser
    try:
        webbrowser.open(url)
    except Exception as e:
        logger.warning(f"打开浏览器时出错: {e}")

def main() -> int:
    """
    主函数，协调整个初始化过程

    返回:
        int: 成功返回0，失败返回非0值
    """
    try:
        # 设置信号处理器
        setup_signal_handlers()

        first_run = is_first_run()

        if first_run:
            logger.info("首次运行，将进行完整初始化...")

            # 检测BetterGI安装路径
            install_path = find_bettergi_install_path()
            setup_env_file(install_path)

            # 安装Python环境
            if not setup_python_env():
                logger.error("Python环境配置失败")
                return 1

        else:
            logger.info("检测到非首次运行，跳过环境配置步骤...")

        # 启动服务器
        backend_server = start_backend_server()
        if backend_server:
            server_processes.append(backend_server)
        else:
            logger.error("后端服务器启动失败")
            return 1


        # 如果是首次运行且成功启动了服务，创建标记文件
        if first_run:
            create_init_marker()

        open_browser("http://localhost:5000")

        logger.info("BetterGI日志分析工具已成功启动，你可以通过 http://localhost:5000 进行访问。")
        logger.info("按Ctrl+C可以终止服务")

        # 等待服务器进程结束
        for process in server_processes:
            process.wait()

        return 0

    except KeyboardInterrupt:
        logger.info("接收到用户中断，正在关闭服务...")
        cleanup_resources()
        return 0
    except Exception as e:
        logger.error(f"初始化过程中发生错误: {e}")
        cleanup_resources()
        return 1
    finally:
        cleanup_resources()


if __name__ == "__main__":
    sys.exit(main())