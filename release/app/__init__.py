"""
应用初始化模块
创建Flask实例并配置应用
"""
from flask import Flask


def create_app(config_name='production'):
    """
    创建Flask应用实例
    
    Args:
        config_name: 配置名称 ('development', 'production', 'testing')
        
    Returns:
        Flask应用实例
    """
    app = Flask(__name__)
    
    # 从配置文件加载配置
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import config, load_env_file
    
    # 根据环境重新加载对应的.env文件
    load_env_file(config_name)
    
    # 根据配置名称选择对应的配置类
    config_class = config.get(config_name, config['default'])
    
    # 创建配置实例并设置到Flask应用
    config_instance = config_class()
    
    # 将配置实例的属性复制到Flask配置中
    for attr_name in dir(config_instance):
        if not attr_name.startswith('_') and not callable(getattr(config_instance, attr_name)):
            # 跳过方法，只复制属性
            if hasattr(config_instance, attr_name):
                value = getattr(config_instance, attr_name)
                app.config[attr_name] = value
    
    # 注册蓝图
    from app.api.views import api_bp
    app.register_blueprint(api_bp)
    
    return app