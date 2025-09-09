import os.path
import os
import re
import logging
import subprocess
import sys
from typing import Optional
from flask import Flask, jsonify, send_from_directory
# from flask_cors import CORS
import threading
import argparse
import time  # 在启动浏览器的时候有一个sleep

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('BetterGI初始化')

# 获取启动参数
parser = argparse.ArgumentParser(description='参量质变仪，用于解析BetterGI日志。')
parser.add_argument('-bgi', '--bgi_path', default=None, help='BetterGI程序路径')
parser.add_argument('-port', '--port', default=3000, help='网页前端使用的本地端口号')
parser.add_argument('-no', '--do_not_open_website', action='store_true', help='默认启动时打开网页，传递此参数以禁用')
args = parser.parse_args()
install_path = args.bgi_path
web_port = args.port
do_not_open_website = args.do_not_open_website
send_png_by_webhook_to_Lark = None


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


def open_browser_after_start():
    """在Flask应用启动后打开浏览器"""

    def target():
        # 等待一段时间，确保Flask服务器完全启动
        time.sleep(2)
        url = 'http://127.0.0.1:3000'
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


if not do_not_open_website:
    open_browser_after_start()
# 检测BetterGI安装路径并设置环境变量
if install_path is None:
    logger.info('正在尝试查找BetterGI安装路径。')
    install_path = find_bettergi_install_path()
    if install_path is None:
        logger.error('未找到BetterGI安装路径。')
        sys.exit(1)
else:
    logger.info(f'已指定BetterGI安装路径为: {install_path}')
# 获取日志目录路径
BGI_LOG_DIR = os.path.join(install_path, 'log')

# 创建Flask应用实例，设置静态文件夹路径为'static'
app = Flask(__name__, static_folder='static')
# 测试前端的时候，使用CORS
# CORS(app)

# ---------------------之后更新的内容粘贴到这里---------------------

# 需要过滤的物品列表
FORBIDDEN_ITEMS = ['调查', '直接拾取']
item_cached_list = []  # 用于替代原有的筛选功能，避免物品的重复记录。
item_datadict = {
    '物品名称': [], '时间': [], '日期': [], '归属配置组': []
}
duration_datadict = {
    '日期': [], '持续时间': []
}
log_list = None
# 预编译正则表达式
LOG_PATTERN = re.compile(r'\[([^]]+)\] \[([^]]+)\] ([^\n]+)\n?([^\n[]*)') # 匹配日支行
TASK_BEGIN_PATTERN = re.compile(r'^配置组 "([^"]*)" 加载完成，共(\d+)个脚本，开始执行$')  # 匹配配置组开始
# 文件保存地址
# 全局变量-当前app.py所在的文件夹路径（不含自己）
script_dir = app.root_path
FILE_SAVE_PATH = os.path.join(script_dir, 'files')
os.makedirs(FILE_SAVE_PATH, exist_ok=True)


def format_timedelta(seconds):
    """
    将秒数转换为中文 x小时y分钟 格式

    Args:
        seconds: 秒数，可以是整数或None

    Returns:
        str: 格式化后的时间字符串，如 "5小时30分钟"
    """
    if seconds is None:
        return "0分钟"

    # 计算小时和分钟
    hours, remainder = divmod(int(seconds), 3600)
    minutes, _ = divmod(remainder, 60)

    # 拼接字符串（忽略零值部分）
    parts = []
    if hours > 0:
        parts.append(f"{hours}小时")
    if minutes > 0:
        parts.append(f"{minutes}分钟")

    return ''.join(parts) if parts else "0分钟"


def parse_timestamp_to_seconds(timestamp):
    """
    将时间戳字符串直接转换为当日的总秒数
    格式: "04:10:02.395" -> 14402.395
    """
    parts = timestamp.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds_parts = parts[2].split('.')
    seconds = int(seconds_parts[0])
    milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0

    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000


def check_dict_empty(dictionary: dict[str:list]) -> bool:
    """
     提供一个方法，判断自定义的字典数据结构是否有误或者为空。有误则抛出错误，
     返回True：为空
     返回False：不为空。
    """
    lengths = {len(lst) for lst in dictionary.values()}
    if len(lengths) > 1:
        # 说明长度不一致
        raise Exception(f"字典数据结构有误，请检查数据结构。对应的长度有{lengths}")
    if lengths == {0}:
        return True
    else:
        return False

def parse_log(log_content, date_str):
    """
    解析日志内容，提取日志类型、交互物品等信息，并统计相关信息。
    支持多次主窗体实例化/退出，自动计算所有段的总时长。

    Args:
        log_content: 日志文件内容
        date_str: 日期字符串

    Returns:
        dict: 包含解析结果的字典
    """
    global item_datadict, duration_datadict
    matches = LOG_PATTERN.findall(log_content)

    # type_count = {}
    # interaction_items = []
    item_count = {}
    duration = 0
    cache_dict = {
        '物品名称': [],
        '时间': [],
        '日期': [],
        '归属配置组': []
    }

    current_start = None  # 当前段开始时间
    current_end = None

    current_task = None # 当前运行的配置组
    for match in matches:
        timestamp = match[0]  # 时间戳
        # level = match[1]  # 日志级别
        # log_type = match[2]  # 类名
        details = match[3].strip()  # 日志内容文本

        # 过滤禁用的关键词
        if any(keyword in details for keyword in FORBIDDEN_ITEMS):
            continue
            # 类型统计
        # type_count[log_type] = type_count.get(log_type, 0) + 1

        # 匹配配置组开始
        task_matches = TASK_BEGIN_PATTERN.match(details)
        if task_matches:
            current_task = task_matches.group(1)
        # 匹配配置组结束
        if not current_task:
            if f'配置组 "{current_task}" 执行结束' in details:
                current_task = None


        # 转换时间戳
        current_time = parse_timestamp_to_seconds(timestamp)
        # 提取拾取内容
        if '交互或拾取' in details:
            item = details.split('：')[1].strip('"')
            # interaction_items.append(item)
            item_count[item] = item_count.get(item, 0) + 1

            # 检查是否存在匹配的行
            existing_row = f'{item}{timestamp}{date_str}{current_task}' in item_cached_list

            # 如果不存在匹配的行，则添加新行
            if not existing_row:
                cache_dict['物品名称'].append(item)
                cache_dict['时间'].append(timestamp)
                cache_dict['日期'].append(date_str)
                cache_dict['归属配置组'].append(str(current_task))
                item_cached_list.append(f'{item}{timestamp}{date_str}{current_task}')

        # 处理时间段
        if not current_start:
            # 开始新的时间段
            current_start = current_time
            current_end = current_time
        else:
            # 计算与上一个有效时间的间隔
            delta = int(current_time - current_end)
            if delta <= 300:
                # 表明是连续的事件，更新结束时间
                current_end = current_time
            else:
                # 表明是一段新的事件
                if delta <= 0:
                    logger.critical(
                        f"时间段错误,请检查。有关参数：{timestamp, details, date_str, current_start, current_end, delta}")
                else:
                    # 累加持续时间
                    duration += int(delta)
                # 开始新的时间段
                current_start = current_time
                current_end = current_time

    # 处理最后一段时间
    if current_start and current_end and current_start != current_end:
        delta = int(current_end - current_start)
        duration += int(delta)

    return {
        # 'type_count': type_count,
        # 'interaction_items': interaction_items,
        # 'interaction_count': len(interaction_items),
        'item_count': item_count,
        # 'delta_time': format_timedelta(duration),
        'duration': duration,
        'cache_dict': cache_dict
    }


def read_log_file(file_path, date_str):
    """
    读取指定路径的日志文件并解析内容。

    Args:
        file_path: 日志文件路径
        date_str: 日期字符串

    Returns:
        dict: 解析后的日志信息字典，若发生错误则返回错误信息
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            log_content = file.read()
        return parse_log(log_content, date_str)
    except FileNotFoundError:
        return {"error": "文件未找到"}
    except Exception as e:
        return {"error": f"发生了一个未知错误: {e}"}


def get_log_list():
    """
    获取日志文件列表，并过滤掉不包含交互物品的日志文件。写入duration_datadict, item_datadict两个全局变量

    Returns:
        list: 过滤后的日志文件名列表
    """
    # 获取所有以'better-genshin-impact'开头的日志文件，并提取日期部分
    log_files = [f.replace('better-genshin-impact', '').replace('.log', '')
                 for f in os.listdir(BGI_LOG_DIR)
                 if f.startswith('better-genshin-impact')]

    filtered_logs = []
    duration_dict = {
        '日期': [],
        '持续时间': []
    }
    cached_dict = {
        '物品名称': [],
        '时间': [],
        '日期': [],
        '归属配置组': []
    }
    for file in log_files:
        file_path = os.path.join(BGI_LOG_DIR, f"better-genshin-impact{file}.log")
        result = read_log_file(file_path, file)
        if not result:
            # 如果结果为空
            continue
        if "error" in result:
            logger.error(f"发生错误:{result['error']}")
            continue

        # 过滤掉不需要的物品
        items = result['item_count'].copy()
        for forbidden_item in FORBIDDEN_ITEMS:
            if forbidden_item in items:
                del items[forbidden_item]

        # 只保留有物品的日志
        if items:
            filtered_logs.append(file)
            duration_dict['日期'].append(file)
            duration_dict['持续时间'].append(result['duration'])
            cached_dict['物品名称'] += result['cache_dict']['物品名称']
            cached_dict['时间'] += result['cache_dict']['时间']
            cached_dict['日期'] += result['cache_dict']['日期']
            cached_dict['归属配置组'] += result['cache_dict']['归属配置组']
    global duration_datadict, item_datadict
    duration_datadict = duration_dict
    item_datadict = cached_dict
    return filtered_logs


# 路由定义
@app.route('/')
def serve_index():
    """
    提供静态资源的路由，返回index.html文件。
    """
    return send_from_directory('static', 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """
    提供静态资源的路由，返回指定的静态文件。
    """
    return send_from_directory('static', filename)


@app.route('/api/LogList', methods=['GET'])
def get_log_list_api():
    """
    提供日志文件列表的API接口。

    Returns:
        JSON: 包含日志文件列表的JSON响应.例如：{'list': ['20250501']}
    """
    global log_list
    if not log_list:
        log_list = get_log_list()
    log_list.reverse()  # 最新的日志排在前面
    return jsonify({'list': log_list})


@app.route('/api/LogData', methods=['GET'])
def analyse_log():
    """
    提供日志分析的API接口，默认返回所有的数据，分析交给前端进行。

    Returns:
        JSON: 包含日志分析结果的JSON响应。例如：{
        'duration': duration_dict,
        'item': item_dict
    }
    """
    if check_dict_empty(duration_datadict) or check_dict_empty(item_datadict):
        get_log_list()

    return jsonify({
        'duration': duration_datadict,
        'item': item_datadict
    })



# 启动Flask应用
if __name__ == "__main__":
    import time

    # t1 = time.time()
    # log_list = get_log_list()
    # with app.app_context():
    #     analyse_duration_history()
    # t2 = time.time()
    # print(t2 - t1, 's')

    # log_list = get_log_list()

    app.run(debug=False, host='0.0.0.0', port=3000, use_reloader=False)

    # with open('1.log','r',encoding='utf-8') as e:
    #     a = e.read()
    # data = parse_log(a,'20250401')
    # print(data)