"""
视图模块
路由映射：定义URL与处理函数的关联
"""
from flask import Blueprint, jsonify, send_from_directory, request , redirect
from app.api.controllers import LogController, WebhookController
import os

# 创建蓝图
api_bp = Blueprint('api', __name__)

# 全局控制器实例（将在应用启动时初始化）
log_controller = None
webhook_controller = None


def init_controllers(log_dir: str):
    """
    初始化控制器
    
    Args:
        log_dir: 日志目录路径
    """
    global log_controller, webhook_controller
    log_controller = LogController(log_dir)
    webhook_controller = WebhookController(log_dir)

@api_bp.route('/')
def index():
    """
    提供主页的API接口，自动跳转到/home路由。
    
    Returns:
        Response: 重定向到/home路由
    """

    return redirect('/home')

@api_bp.route('/home')
def serve_index():
    """
    提供静态资源的路由，返回index.html文件。
    
    Returns:
        Response: index.html文件响应
    """
    return send_from_directory('static', 'index.html')


@api_bp.route('/<path:filename>')
def serve_static(filename):
    """
    提供静态资源的路由，返回指定的静态文件。
    
    Args:
        filename: 静态文件名
        
    Returns:
        Response: 静态文件响应
    """
    return send_from_directory('static', filename)


@api_bp.route('/api/LogList', methods=['GET'])
def get_log_list_api():
    """
    提供日志文件列表的API接口。

    Returns:
        Response: 包含日志文件列表的JSON响应，例如：{'list': ['20250501']}
    """
    if not log_controller:
        return jsonify({'error': '控制器未初始化'}), 500
    
    result = log_controller.get_log_list()
    return jsonify(result)


@api_bp.route('/api/LogData', methods=['GET'])
def analyse_log():
    """
    提供日志分析的API接口，默认返回所有的数据，分析交给前端进行。

    Returns:
        Response: 包含日志分析结果的JSON响应，例如：{
            'duration': duration_dict,
            'item': item_dict
        }
    """
    if not log_controller:
        return jsonify({'error': '控制器未初始化'}), 500
    
    result = log_controller.get_log_data()
    return jsonify(result)


@api_bp.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook接口，接收POST请求并保存数据
    
    Returns:
        Response: 包含操作结果的JSON响应，例如：{
            'success': True,
            'message': '数据保存成功'
        }
    """
    if not webhook_controller:
        return jsonify({'success': False, 'message': 'Webhook控制器未初始化'}), 500
    
    try:
        # 获取POST请求的JSON数据
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'}), 400
        
        # 调用控制器保存数据
        result = webhook_controller.save_data(data)
        
        # 根据结果返回相应的HTTP状态码
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'处理请求时发生错误: {str(e)}'
        }), 500


@api_bp.route('/api/webhook-data', methods=['GET'])
def get_webhook_data():
    """
    获取webhook数据列表的API接口
    
    Returns:
        Response: 包含webhook数据列表的JSON响应
    """
    if not webhook_controller:
        return jsonify({'success': False, 'message': 'Webhook控制器未初始化'}), 500
    
    try:
        # 获取查询参数
        limit = request.args.get('limit', 100, type=int)
        
        # 调用控制器获取数据
        result = webhook_controller.get_webhook_data(limit)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取数据时发生错误: {str(e)}',
            'data': [],
            'count': 0
        }), 500