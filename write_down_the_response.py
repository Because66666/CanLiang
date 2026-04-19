import flask
from flask import request, jsonify
import os
import time
import json

app = flask.Flask(__name__)
fold = 'response_test'

def write_down_response(data: dict):
    if not os.path.exists(fold):
        os.makedirs(fold)
    with open(os.path.join(fold, f'response_{int(time.time())}.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    write_down_response(data)
    return 'success', 200

if __name__ == '__main__':
    print('服务器已经运行，请在Bgi中填入地址：http://127.0.0.1:5000')
    app.run(debug=True)