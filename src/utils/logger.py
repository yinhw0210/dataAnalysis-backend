import os
import logging
import logging.handlers
from datetime import datetime

# 导入配置模块
from .config import config

# 确保日志目录存在
os.makedirs(config.LOG_DIR, exist_ok=True)

# 获取日志级别
def get_log_level(level_name: str) -> int:
    """将日志级别名称转换为日志级别值"""
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    return level_map.get(level_name.upper(), logging.INFO)

# 日志文件命名
def get_log_filename(name):
    """根据名称和日期生成日志文件名"""
    today = datetime.now().strftime('%Y-%m-%d')
    return os.path.join(config.LOG_DIR, f'{name}_{today}.log')

def setup_logger(name, log_level=None):
    """
    设置并返回命名的日志器
    
    参数:
        name: 日志器名称
        log_level: 日志级别，如果为None则使用配置中的值
    
    返回:
        配置好的日志器实例
    """
    # 如果未指定日志级别，使用配置中的值
    if log_level is None:
        log_level = get_log_level(config.LOG_LEVEL)
        
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 防止日志重复
    if logger.handlers:
        return logger
    
    # 创建按日期滚动的文件处理器
    file_handler = logging.handlers.TimedRotatingFileHandler(
        get_log_filename(name),
        when='midnight',
        interval=1,
        backupCount=config.LOG_BACKUP_COUNT  # 保留的日志文件数
    )
    file_handler.setLevel(log_level)
    
    # 设置格式
    formatter = logging.Formatter(config.LOG_FORMAT, config.LOG_DATE_FORMAT)
    file_handler.setFormatter(formatter)
    
    # 将处理器添加到日志器
    logger.addHandler(file_handler)
    
    # 阻止日志传递到根日志器（根日志器可能会输出到控制台）
    logger.propagate = False
    
    return logger

# 为不同模块创建日志器
def get_app_logger():
    """获取应用主日志器"""
    return setup_logger('app')

def get_test_logger():
    """获取测试模块日志器"""
    return setup_logger('test')

def get_utils_logger():
    """获取工具模块日志器"""
    return setup_logger('utils')

def get_global_logger():
    """获取系统模块日志器"""
    return setup_logger('global')

def get_analyze_logger():
    """获取分析模块日志器"""
    return setup_logger('analyze')

def get_inpainting_logger():
    """获取图像修复模块日志器"""
    return setup_logger('inpainting')

# 配置根日志器，确保未捕获的日志也被记录
def configure_root_logger():
    """配置根日志器，将所有未捕获的日志记录到文件"""
    root_logger = logging.getLogger()
    log_level = get_log_level(config.LOG_LEVEL)
    root_logger.setLevel(log_level)
    
    # 移除所有已有的处理器（如控制台处理器）
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加文件处理器
    file_handler = logging.handlers.TimedRotatingFileHandler(
        get_log_filename('system'),
        when='midnight',
        interval=1,
        backupCount=config.LOG_BACKUP_COUNT
    )
    file_handler.setLevel(log_level)
    
    formatter = logging.Formatter(config.LOG_FORMAT, config.LOG_DATE_FORMAT)
    file_handler.setFormatter(formatter)
    
    root_logger.addHandler(file_handler)
    
    return root_logger

# 初始化根日志器
configure_root_logger() 