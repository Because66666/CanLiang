import os.path
import re
from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv
from datetime import *
from collections import defaultdict
import re
from datetime import datetime, timedelta

# 加载环境变量
load_dotenv()

# 获取日志目录路径
bgi_logdir = os.path.join(os.getenv('BETTERGI_PATH'), 'log')

# 创建Flask应用实例，设置静态文件夹路径为'static'
app = Flask(__name__, static_folder='static')


def format_timedelta(td) -> str:
    """将 timedelta 对象格式化为 'X小时Y分钟' 的形式"""
    if td is None:
        return "0分钟"
    # 计算总秒数
    total_seconds = td

    # 计算小时和分钟
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    # 拼接字符串（忽略零值部分）
    parts = []
    if hours > 0:
        parts.append(f"{hours}小时")
    if minutes > 0:
        parts.append(f"{minutes}分钟")

    return ''.join(parts) if parts else "0分钟"

def format_timedelta(seconds):
    """将秒数转换为中文 x小时y分钟 格式"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}小时{minutes}分钟"

def parse_log(log_content):
    """
    解析日志内容，提取日志类型、交互物品等信息，并统计相关信息。
    支持多次主窗体实例化/退出，自动计算所有段的总时长。
    """
    log_pattern = r'\[([^]]+)\] \[([^]]+)\] ([^\n]+)\n?([^\n[]*)'
    matches = re.findall(log_pattern, log_content)

    type_count = {}
    interaction_items = []
    item_count = {}
    duration = 0

    current_start = None  # 当前段开始时间

    for match in matches:
        timestamp = match[0]  # 时间戳
        level = match[1]      # 日志级别
        log_type = match[2]   # 类名
        details = match[3].strip()  # 日志内容文本

        # 类型统计
        type_count[log_type] = type_count.get(log_type, 0) + 1

        # 提取拾取内容
        if '交互或拾取' in details:
            item = details.split('：')[1].strip('"')
            interaction_items.append(item)
            item_count[item] = item_count.get(item, 0) + 1

        # 处理时间段
        elif '主窗体实例化' in details:
            current_start = datetime.strptime(timestamp, '%H:%M:%S.%f')

        elif ('主窗体退出' in details or '将执行 关机' in details) and current_start:
            current_end = datetime.strptime(timestamp, '%H:%M:%S.%f')
            delta = (current_end - current_start).total_seconds()
            duration += int(delta)
            current_start = None  # 清除开始时间，准备下一段

    return {
        'type_count': type_count,
        'interaction_items': interaction_items,
        'interaction_count': len(interaction_items),
        'item_count': item_count,
        'delta_time': format_timedelta(duration)
    }

# # 解析日志内容的函数
# def parse_log(log_content):
#     """
#     解析日志内容，提取日志类型、交互物品等信息，并统计相关信息。
#     :param log_content: 日志内容字符串
#     :return: 包含日志类型统计、交互物品列表、交互物品统计等信息的字典
#     """
#     log_pattern = r'\[([^]]+)\] \[([^]]+)\] ([^\n]+)\n?([^\n[]*)'
#     matches = re.findall(log_pattern, log_content)

#     type_count = {}
#     interaction_items = []
#     start_time = None
#     end_time = None
#     duration = 0

#     for match in matches:
#         timestamp = match[0]
#         level = match[1]
#         log_type = match[2]
#         details = match[3].strip()

#         # 统计每种类型的出现次数
#         if log_type in type_count:
#             type_count[log_type] += 1
#         else:
#             type_count[log_type] = 1

#         # 提取交互或拾取的物品
#         if '交互或拾取' in details:
#             item = details.split('：')[1].strip('"')
#             interaction_items.append(item)
#         elif '主窗体实例化' in details:
#             if start_time is None:
#                 start_time = datetime.strptime(timestamp, '%H:%M:%S.%f')
#         elif '主窗体退出' in details or '将执行 关机' in details:
#             end_time = datetime.strptime(timestamp, '%H:%M:%S.%f')



#     # 统计交互或拾取物品中每个字符串出现的次数
#     item_count = {}
#     for item in interaction_items:
#         if item in item_count:
#             item_count[item] += 1
#         else:
#             item_count[item] = 1

#     if start_time and end_time:
#         duration = duration + (end_time - start_time).seconds
#     return {
#         'type_count': type_count,
#         'interaction_items': interaction_items,
#         'interaction_count': len(interaction_items),
#         'item_count': item_count,
#         'delta_time': format_timedelta(duration)
#     }


# 读取日志文件并解析内容
def read_log_file(file_path):
    """
    读取指定路径的日志文件并解析内容。
    :param file_path: 日志文件路径
    :return: 解析后的日志信息字典，若发生错误则返回错误信息
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            log_content = file.read()
        return parse_log(log_content)
    except FileNotFoundError:
        return {"error": "文件未找到"}
    except Exception as e:
        return {"error": f"发生了一个未知错误: {e}"}


# 获取日志文件列表
def get_log_list():
    """
    获取日志文件列表，并过滤掉不包含交互物品的日志文件。
    :return: 过滤后的日志文件名列表
    """
    l = [f.replace('better-genshin-impact', '').replace('.log', '') for f in os.listdir(bgi_logdir) if
         f.startswith('better-genshin-impact')]
    l2 = []
    for file in l:
        file_path = os.path.join(bgi_logdir, f"better-genshin-impact{file}.log")
        result = read_log_file(file_path)
        if "error" in result:
            continue
        items = result['item_count']
        if '调查' in items:
            del items['调查']
        if len(items) == 0:
            continue
        l2.append(file)
    return l2


# 提供静态资源的路由
@app.route('/')
def serve_index():
    """
    提供静态资源的路由，返回index.html文件。
    """
    return send_from_directory('static', 'index.html')


# 提供静态资源的路由
@app.route('/<path:filename>')
def serve_static(filename):
    """
    提供静态资源的路由，返回指定的静态文件。
    """
    return send_from_directory('static', filename)


# 提供日志文件列表的API接口
@app.route('/api/LogList', methods=['GET'])
def get_log_list_api():
    """
    提供日志文件列表的API接口。
    :return: 包含日志文件列表的JSON响应
    """
    # 获取日志文件列表
    log_list = get_log_list()
    log_list.reverse()
    return jsonify({'list': log_list})

# 解析 duration 函数
def parse_duration(duration_str):
    match = re.match(r"(\d+)小时(\d+)分钟", duration_str)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        return hours, minutes
    else:
        return 0, 0
    
# 提供日志分析的API接口
@app.route('/api/analyse', methods=['GET'])
def analyse_log():
    """
    提供日志分析的API接口，返回指定日期的日志分析结果。
    :return: 包含日志分析结果的JSON响应
    """
    date = request.args.get('date', 'all')
    print(date)
    if date == 'all':
        # 初始化总和
        total_hours = 0
        total_minutes = 0

        total_response = {
            "duration": "",
            "item_count": defaultdict(int)  # 自动初始化新 key 为 0
        }
        for filename in os.listdir(bgi_logdir):
            if filename.endswith(".log"):
                file_path = os.path.join(bgi_logdir, filename)
                result = read_log_file(file_path)
                if "error" in result:
                    continue
                items = result['item_count']
                forbidden = ['调查', '直接拾取']
                for keyword in forbidden:
                    if keyword in items:
                        del items[keyword]
                sample_response = {
                    'item_count': items,
                    'duration': result['delta_time']
                }
                # 累加 item_count
                for key in sample_response["item_count"]:
                    total_response["item_count"][key] += sample_response["item_count"][key]

                # 累加 duration
                h, m = parse_duration(sample_response["duration"])
                total_hours += h
                total_minutes += m
        # 处理分钟进位
        total_hours += total_minutes // 60
        total_minutes = total_minutes % 60

        # 设置总 duration 字符串
        total_response["duration"] = f"{total_hours}小时{total_minutes}分钟"        
        # for i in range(10):
        #     print(date)
        # response = {
        #     'item_count': 1,
        #     'duration': 1
        # }
        return jsonify(total_response)
    else:
        file_path = os.path.join(bgi_logdir, f"better-genshin-impact{date}.log")
        result = read_log_file(file_path)

        if "error" in result:
            return jsonify(result), 400
        items = result['item_count']
        forbidden = ['调查', '直接拾取']
        for keyword in forbidden:
            if keyword in items:
                del items[keyword]
        response = {
            'item_count': items,
            'duration': result['delta_time']
        }
        return jsonify(response)
    


# 启动Flask应用
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
