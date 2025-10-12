"""
配置文件
数据库、Flask等配置
支持.env文件加载（如果python-dotenv库可用）
"""
import os
import logging

# 尝试导入python-dotenv库，如果不存在则跳过
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


def load_env_file(environment='production'):
    """
    根据环境加载对应的.env文件
    
    Args:
        environment (str): 环境名称 ('development', 'production', 'testing')
    """
    if not DOTENV_AVAILABLE:
        print("警告: python-dotenv库未安装，无法加载.env文件")
        return
    
    # 环境文件映射
    env_files = {
        'development': '.env.development',
        'production': '.env.production', 
        'testing': '.env.testing'
    }
    
    # 获取对应的环境文件
    env_file = env_files.get(environment, '.env.production')
    
    # 检查文件是否存在
    if os.path.exists(env_file):
        # 使用override=True来覆盖已存在的环境变量
        load_dotenv(env_file, override=True)
        print(f"已加载环境配置文件: {env_file}")
    else:
        print(f"警告: 环境配置文件 {env_file} 不存在")


# 默认加载生产环境配置，实际环境将在create_app中重新加载
load_env_file('production')


class Config:
    """
    应用配置基类
    包含Flask应用的各种配置参数
    
    配置优先级：环境变量 > 子类配置 > 基础配置
    如果python-dotenv库可用，会自动加载.env文件中的环境变量
    """
    
    @property
    def SECRET_KEY(self):
        return os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    @property
    def DEBUG(self):
        return os.environ.get('DEBUG', 'false').lower() == 'true'
    
    @property
    def HOST(self):
        return os.environ.get('HOST', '0.0.0.0')
    
    @property
    def PORT(self):
        return int(os.environ.get('PORT', '3000'))
    
    @property
    def LOG_LEVEL(self):
        return getattr(logging, os.environ.get('LOG_LEVEL', 'INFO').upper(), logging.INFO)
    
    @property
    def LOG_FORMAT(self):
        return os.environ.get('LOG_FORMAT', '%(asctime)s - %(levelname)s - %(message)s')
    
    @property
    def LOG_DATE_FORMAT(self):
        return os.environ.get('LOG_DATE_FORMAT', '%Y-%m-%d %H:%M:%S')
    
    @property
    def BGI_INSTALL_PATH(self):
        return os.environ.get('BGI_INSTALL_PATH')
    
    @property
    def FILE_SAVE_PATH(self):
        return os.environ.get('FILE_SAVE_PATH', 'files')
    
    @property
    def STATIC_FOLDER(self):
        return os.environ.get('STATIC_FOLDER', 'static')
    
    @property
    def ENABLE_CORS(self):
        return os.environ.get('ENABLE_CORS', 'false').lower() == 'true'
    
    @staticmethod
    def init_app(app):
        """
        初始化应用配置
        
        Args:
            app: Flask应用实例
        """
        # 获取配置实例
        config_instance = app.config
        
        # 配置日志
        log_level = config_instance.get('LOG_LEVEL', logging.INFO)
        log_format = config_instance.get('LOG_FORMAT', '%(asctime)s - %(levelname)s - %(message)s')
        log_date_format = config_instance.get('LOG_DATE_FORMAT', '%Y-%m-%d %H:%M:%S')
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            datefmt=log_date_format
        )
        
        # 创建文件保存目录
        file_save_path = os.path.join(app.root_path, config_instance.get('FILE_SAVE_PATH', 'files'))
        os.makedirs(file_save_path, exist_ok=True)
        
        # 配置CORS
        enable_cors = config_instance.get('ENABLE_CORS', False)
        if enable_cors:
            try:
                from flask_cors import CORS
                CORS(app)
                app.logger.info("CORS已启用")
            except ImportError:
                app.logger.warning("flask-cors未安装，无法启用CORS支持")
        
        # 记录配置状态
        logger = logging.getLogger(__name__)
        if DOTENV_AVAILABLE:
            logger.info(".env文件支持已启用")
        else:
            logger.info(".env文件支持未启用（python-dotenv库未安装）")


class DevelopmentConfig(Config):
    """
    开发环境配置
    """
    @property
    def SECRET_KEY(self):
        return os.environ.get('SECRET_KEY', 'dev-secret-key-for-development')
    
    @property
    def DEBUG(self):
        return os.environ.get('DEBUG', 'true').lower() == 'true'
    
    @property
    def HOST(self):
        return os.environ.get('HOST', '127.0.0.1')
    
    @property
    def PORT(self):
        return int(os.environ.get('PORT', '3001'))  # 开发环境默认端口3001
    
    @property
    def LOG_LEVEL(self):
        return getattr(logging, os.environ.get('LOG_LEVEL', 'DEBUG').upper(), logging.DEBUG)
    
    @property
    def BGI_INSTALL_PATH(self):
        return os.environ.get('BGI_INSTALL_PATH')
    
    @property
    def ENABLE_CORS(self):
        return os.environ.get('ENABLE_CORS', 'true').lower() == 'true'


class ProductionConfig(Config):
    """
    生产环境配置
    """
    @property
    def SECRET_KEY(self):
        return os.environ.get('SECRET_KEY', 'CHANGE-THIS-IN-PRODUCTION')
    
    @property
    def DEBUG(self):
        return os.environ.get('DEBUG', 'false').lower() == 'true'
    
    @property
    def HOST(self):
        return os.environ.get('HOST', '0.0.0.0')
    
    @property
    def PORT(self):
        return int(os.environ.get('PORT', '3000'))
    
    @property
    def LOG_LEVEL(self):
        return getattr(logging, os.environ.get('LOG_LEVEL', 'INFO').upper(), logging.INFO)
    
    @property
    def BGI_INSTALL_PATH(self):
        return os.environ.get('BGI_INSTALL_PATH')
    
    @property
    def ENABLE_CORS(self):
        return os.environ.get('ENABLE_CORS', 'false').lower() == 'true'


class TestingConfig(Config):
    """
    测试环境配置
    """
    @property
    def SECRET_KEY(self):
        return os.environ.get('SECRET_KEY', 'test-secret-key')
    
    @property
    def DEBUG(self):
        return os.environ.get('DEBUG', 'true').lower() == 'true'
    
    @property
    def TESTING(self):
        return True
    
    @property
    def HOST(self):
        return os.environ.get('HOST', '127.0.0.1')
    
    @property
    def PORT(self):
        return int(os.environ.get('PORT', '3001'))  # 使用不同端口避免冲突
    
    @property
    def LOG_LEVEL(self):
        return getattr(logging, os.environ.get('LOG_LEVEL', 'DEBUG').upper(), logging.DEBUG)
    
    @property
    def BGI_INSTALL_PATH(self):
        return os.environ.get('BGI_INSTALL_PATH')
    
    @property
    def FILE_SAVE_PATH(self):
        return os.environ.get('FILE_SAVE_PATH', 'test_files')
    
    @property
    def ENABLE_CORS(self):
        return os.environ.get('ENABLE_CORS', 'true').lower() == 'true'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}