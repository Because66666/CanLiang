import os.path
import re
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
bgi_logdir = os.path.join(os.getenv('BETTERGI_PATH'), 'log')
app = Flask(__name__)
CORS(app)


def parse_log(log_content):
    log_pattern = r'\[([^]]+)\] \[([^]]+)\] ([^\n]+)\n?([^\n[]*)'
    matches = re.findall(log_pattern, log_content)

    type_count = {}
    interaction_items = []

    for match in matches:
        timestamp = match[0]
        level = match[1]
        log_type = match[2]
        details = match[3].strip()

        # 统计每种类型的出现次数
        if log_type in type_count:
            type_count[log_type] += 1
        else:
            type_count[log_type] = 1

        # 提取交互或拾取的物品
        if '交互或拾取' in details:
            item = details.split('：')[1].strip('"')
            interaction_items.append(item)

    # 统计交互或拾取物品中每个字符串出现的次数
    item_count = {}
    for item in interaction_items:
        if item in item_count:
            item_count[item] += 1
        else:
            item_count[item] = 1

    return {
        'type_count': type_count,
        'interaction_items': interaction_items,
        'interaction_count': len(interaction_items),
        'item_count': item_count
    }


def read_log_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            log_content = file.read()
        return parse_log(log_content)
    except FileNotFoundError:
        return {"error": "文件未找到"}
    except Exception as e:
        return {"error": f"发生了一个未知错误: {e}"}


def get_log_list():
    l = [f.replace('better-genshin-impact','').replace('.log','') for f in os.listdir(bgi_logdir) if f.startswith('better-genshin-impact')]
    l2 = []
    for file in l:
        file_path = os.path.join(bgi_logdir, f"better-genshin-impact{file}.log")
        result = read_log_file(file_path)
        if "error" in result:
            continue
        items = result['item_count']
        if '调查' in items:
            del items['调查']
        if len(items)==0:
            continue
        l2.append(file)
    return l2
log_list = get_log_list()
log_list.reverse()

@app.route('/api/LogList', methods=['GET'])
def get_log_list_api():
    global log_list
    # print(log_list)
    return jsonify({'list': log_list})


@app.route('/api/analyse', methods=['GET'])
def analyse_log():
    date = request.args.get('date', '20250430')
    file_path = os.path.join(bgi_logdir, f"better-genshin-impact{date}.log")
    result = read_log_file(file_path)

    if "error" in result:
        return jsonify(result), 400
    items = result['item_count']
    if '调查' in items:
        del items['调查']
    # 提取用户指定的两部分内容
    response = {
        # 'type_count': result['type_count'],  # 对应 L51-53 中的内容
        'item_count': items  # 对应 L66-68 中的内容
    }
    # print('len:',len(items))

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
