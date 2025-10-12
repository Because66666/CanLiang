"""
视图模块
路由映射：定义URL与处理函数的关联
"""
from flask import Blueprint, jsonify, send_from_directory
from app.api.controllers import LogController
import os

# 创建蓝图
api_bp = Blueprint('api', __name__)

# 全局控制器实例（将在应用启动时初始化）
log_controller = None


def init_controllers(log_dir: str):
    """
    初始化控制器
    
    Args:
        log_dir: 日志目录路径
    """
    global log_controller
    log_controller = LogController(log_dir)


@api_bp.route('/')
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