"""
应用入口文件
启动Flask应用

使用方法:
    python run.py                              # 使用生产环境配置启动
    python run.py -env development             # 使用开发环境配置启动
    python run.py -env testing                 # 使用测试环境配置启动
    python run.py -bgi "C:\\BetterGI"          # 指定BetterGI安装路径
    python run.py -ssl "cert.pem,key.pem"     # 启用SSL支持（分离的证书和私钥文件）
    python run.py -ssl "combined.pem"         # 启用SSL支持（包含证书和私钥的单个文件）
    python run.py -no                          # 启动时不自动打开浏览器

环境配置说明:
    - production: 生产环境，默认端口3000，关闭调试模式，关闭CORS
    - development: 开发环境，默认端口3000，开启调试模式，开启CORS
    - testing: 测试环境，默认端口3001，开启调试模式，开启CORSgb

SSL配置说明:
    - 支持两种格式的SSL证书配置：
      1. 分离文件：-ssl "cert.pem,key.pem" （证书文件和私钥文件分开）
      2. 合并文件：-ssl "combined.pem" （证书和私钥在同一个文件中）
    - 启用SSL后，应用将使用HTTPS协议运行
    - 确保证书文件路径正确且文件存在
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
    parser.add_argument('-ssl', '--ssl_cert', default=None, 
                       help='SSL证书文件路径，格式为"cert.pem,key.pem"或单个.pem文件路径')
    # parser.add_argument('-no', '--do_not_open_website', action='store_true', 
    #                    help='默认启动时打开网页，传递此参数以禁用')
    return parser.parse_args()


def parse_ssl_cert(ssl_cert_path):
    """
    解析SSL证书路径参数
    
    Args:
        ssl_cert_path: SSL证书路径，可以是单个.pem文件或"cert.pem,key.pem"格式
        
    Returns:
        tuple: (cert_file, key_file) 或 None
        
    Raises:
        ValueError: 当证书文件不存在或格式错误时
    """
    if not ssl_cert_path:
        return None
        
    # 检查是否为逗号分隔的格式
    if ',' in ssl_cert_path:
        cert_file, key_file = ssl_cert_path.split(',', 1)
        cert_file = cert_file.strip()
        key_file = key_file.strip()
        
        # 验证文件是否存在
        if not os.path.exists(cert_file):
            raise ValueError(f"SSL证书文件不存在: {cert_file}")
        if not os.path.exists(key_file):
            raise ValueError(f"SSL私钥文件不存在: {key_file}")
            
        return (cert_file, key_file)
    else:
        # 单个.pem文件，包含证书和私钥
        ssl_cert_path = ssl_cert_path.strip()
        if not os.path.exists(ssl_cert_path):
            raise ValueError(f"SSL证书文件不存在: {ssl_cert_path}")
            
        return ssl_cert_path


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
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 解析SSL证书配置
        ssl_context = None
        if args.ssl_cert:
            try:
                ssl_config = parse_ssl_cert(args.ssl_cert)
                if ssl_config:
                    logger.info(f"启用SSL支持，证书配置: {args.ssl_cert}")
                    ssl_context = ssl_config
            except ValueError as e:
                logger.error(f"SSL证书配置错误: {e}")
                sys.exit(1)
        
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
        
        # 初始化控制器（不再需要target_app参数）
        init_controllers(bgi_log_dir)
        
        # 如果不禁用，则启动浏览器
        # if not args.do_not_open_website:
        #     open_browser_after_start(port)
        
        # 启动Flask应用
        logger.info(f"启动Flask应用，环境: {args.environment}，端口: {port}")
        if ssl_context:
            logger.info("使用HTTPS模式启动应用")
            app.run(
                debug=config_instance.DEBUG,
                host=config_instance.HOST,
                port=port,
                use_reloader=False,
                ssl_context=ssl_context
            )
        else:
            logger.info("使用HTTP模式启动应用")
            app.run(
                debug=config_instance.DEBUG,
                host=config_instance.HOST,
                port=port,
                use_reloader=False
            )
        
    except KeyboardInterrupt:
        logger.info("接收到键盘中断信号，正在清理资源...")
        cleanup_resources()
        logger.info("资源清理完成，程序退出")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行时发生错误: {e}")
        cleanup_resources()
        sys.exit(1)


def cleanup_resources():
    """
    清理资源的函数
    """
    try:
        # 导入并清理推流控制器
        from app.api.views import stream_controller
        if stream_controller and stream_controller.is_streaming:
            logger.info("正在停止推流...")
            stream_controller.stop_stream()
            logger.info("推流已停止")
    except Exception as e:
        logger.error(f"清理推流资源时发生错误: {e}")
    
    try:
        # 清理其他可能的资源
        logger.info("清理其他资源...")
        # 这里可以添加其他需要清理的资源
    except Exception as e:
        logger.error(f"清理其他资源时发生错误: {e}")


if __name__ == "__main__":
    main()