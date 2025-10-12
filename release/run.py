"""
应用入口文件
启动Flask应用

使用方法:
    python run.py                              # 使用生产环境配置启动
    python run.py -env development             # 使用开发环境配置启动
    python run.py -env testing                 # 使用测试环境配置启动
    python run.py -bgi "C:\\BetterGI"          # 指定BetterGI安装路径
    python run.py -no                          # 启动时不自动打开浏览器

环境配置说明:
    - production: 生产环境，默认端口3000，关闭调试模式，关闭CORS
    - development: 开发环境，默认端口3000，开启调试模式，开启CORS
    - testing: 测试环境，默认端口3001，开启调试模式，开启CORS
"""
import os
import sys
import argparse
import logging
from app import create_app
from app.api.views import init_controllers
from app.infrastructure.utils import find_bettergi_install_path, open_browser_after_start
from config import Config

# 配置日志
logger = logging.getLogger('BetterGI初始化')


def parse_arguments():
    """
    解析命令行参数
    
    Returns:
        argparse.Namespace: 解析后的参数对象
    """
    parser = argparse.ArgumentParser(description='参量质变仪，用于解析BetterGI日志。')
    parser.add_argument('-bgi', '--bgi_path', default=None, help='BetterGI程序路径')
    parser.add_argument('-env', '--environment', default='production', 
                       choices=['development', 'production', 'testing'],
                       help='运行环境 (development/production/testing)，默认为production')
    parser.add_argument('-no', '--do_not_open_website', action='store_true', 
                       help='默认启动时打开网页，传递此参数以禁用')
    return parser.parse_args()


def setup_bgi_path(install_path):
    """
    设置BetterGI安装路径
    
    Args:
        install_path: 指定的安装路径，如果为None则自动检测
        
    Returns:
        str: BetterGI安装路径
        
    Raises:
        SystemExit: 当无法找到BetterGI安装路径时退出程序
    """
    if install_path is None:
        logger.info('正在尝试查找BetterGI安装路径。')
        install_path = find_bettergi_install_path()
        if install_path is None:
            logger.error('未找到BetterGI安装路径。')
            sys.exit(1)
    else:
        logger.info(f'已指定BetterGI安装路径为: {install_path}')
    
    return install_path


def main():
    """
    主函数，启动Flask应用
    """
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置BetterGI安装路径
    install_path = setup_bgi_path(args.bgi_path)
    bgi_log_dir = os.path.join(install_path, 'log')
    
    # 根据环境参数创建Flask应用
    app = create_app(args.environment)
    
    # 初始化配置
    from config import config
    config_class = config.get(args.environment, config['default'])
    config_class.init_app(app)
    
    # 从配置实例获取端口
    config_instance = config_class()
    port = config_instance.PORT
    
    # 初始化控制器
    init_controllers(bgi_log_dir)
    
    # 如果不禁用，则启动浏览器
    if not args.do_not_open_website:
        open_browser_after_start(port)
    
    # 启动Flask应用
    logger.info(f"启动Flask应用，环境: {args.environment}，端口: {port}")
    app.run(
        debug=config_instance.DEBUG,
        host=config_instance.HOST,
        port=port,
        use_reloader=False
    )


if __name__ == "__main__":
    main()