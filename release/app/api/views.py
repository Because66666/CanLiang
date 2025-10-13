"""
视图模块
路由映射：定义URL与处理函数的关联
"""
from flask import Blueprint, jsonify, send_from_directory, request , redirect
from app.api.controllers import LogController, WebhookController, StreamController
import os

# 创建蓝图
api_bp = Blueprint('api', __name__)

# 全局控制器实例（将在应用启动时初始化）
log_controller = None
webhook_controller = None
stream_controller = None


def init_controllers(log_dir: str):
    """
    初始化控制器
    
    Args:
        log_dir: 日志目录路径
    """
    global log_controller, webhook_controller, stream_controller
    log_controller = LogController(log_dir)
    webhook_controller = WebhookController(log_dir)
    # stream_controller将在首次请求时动态创建



@api_bp.route('/')
def serve_index():
    """
    提供静态资源的路由，返回index.html文件。
    
    Returns:
        Response: index.html文件响应
    """
    return send_from_directory('static', 'index.html')

@api_bp.route('/home')
def serve_home():
    """
    提供静态资源的路由，返回 home.html文件。
    
    Returns:
        Response: home.html文件响应
    """
    return send_from_directory('static', 'home.html')

@api_bp.route('/about')
def serve_about():
    """
    提供静态资源的路由，返回 about.html文件。
    
    Returns:
        Response: about.html文件响应
    """
    return send_from_directory('static', 'about.html')

@api_bp.route('/webinfo')
def serve_webinfo():
    """
    提供静态资源的路由，返回 webinfo.html文件。
    
    Returns:
        Response: webinfo.html文件响应
    """
    return send_from_directory('static', 'webinfo.html')





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


@api_bp.route('/api/stream', methods=['GET'])
def video_stream():
    """
    视频流API接口，提供实时屏幕推流
    支持通过查询参数?app=xxx动态指定目标应用程序
    
    Returns:
        Response: MJPEG视频流响应或JSON错误响应
    """
    global stream_controller
    
    # 获取查询参数中的app参数
    target_app = request.args.get('app', '').strip()
    
    # 参数验证
    if not target_app:
        return jsonify({
            'error': '缺少必需的参数',
            'message': '请通过查询参数?app=应用程序名称指定目标应用程序',
            'example': '/api/stream?app=yuanshen.exe'
        }), 400
    
    # 验证应用程序名称格式
    if not target_app.endswith('.exe'):
        return jsonify({
            'error': '参数格式错误',
            'message': '应用程序名称必须以.exe结尾',
            'provided': target_app,
            'example': 'yuanshen.exe'
        }), 400
    
    try:
        # 检查是否需要重新初始化stream_controller
        if not stream_controller or stream_controller.target_app != target_app:
            # 如果当前有推流在进行，先停止
            if stream_controller and stream_controller.is_streaming:
                stream_controller.stop_stream()
            
            # 重新初始化推流控制器
            stream_controller = StreamController(target_app)
        
        return stream_controller.start_stream()
        
    except Exception as e:
        return jsonify({
            'error': f'启动视频流时发生错误: {str(e)}'
        }), 500


@api_bp.route('/api/stream/info', methods=['GET'])
def get_stream_info():
    """
    获取推流信息的API接口
    
    Returns:
        Response: 包含推流状态信息的JSON响应
    """
    if not stream_controller:
        return jsonify({'error': '推流控制器未初始化'}), 500
    
    try:
        result = stream_controller.get_stream_info()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'error': f'获取推流信息时发生错误: {str(e)}'
        }), 500


@api_bp.route('/api/stream/stop', methods=['POST'])
def stop_stream():
    """
    停止推流的API接口
    
    Returns:
        Response: 操作结果的JSON响应
    """
    if not stream_controller:
        return jsonify({'error': '推流控制器未初始化'}), 500
    
    try:
        stream_controller.stop_stream()
        return jsonify({
            'success': True,
            'message': '推流已停止'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'停止推流时发生错误: {str(e)}'
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


@api_bp.route('/api/programlist', methods=['GET'])
def get_program_list():
    """
    获取当前桌面上可以被推流的程序窗口列表的API接口
    
    Returns:
        Response: 包含程序列表的JSON响应，格式为：{
            'success': True,
            'data': ['program1.exe', 'program2.exe', ...],
            'count': 程序数量
        }
    """
    try:
        # 创建临时的StreamController实例来获取程序列表
        temp_controller = StreamController()
        programs = temp_controller.get_available_programs()

        # 创建允许的程序列表
        allowed_programs = [
            'yuanshen.exe',
            'bettergi.exe'
        ]
        programs = [program for program in programs if program in allowed_programs]

        # 自定义的桌面映射
        programs.append('桌面.exe')
        
        return jsonify({
            'success': True,
            'data': programs,
            'count': len(programs),
            'message': f'成功获取到 {len(programs)} 个可推流的程序'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'data': [],
            'count': 0,
            'message': f'获取程序列表时发生错误: {str(e)}'
        }), 500