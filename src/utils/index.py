import re
from typing import Optional
import datetime
from .logger import get_utils_logger

__all__ = ["find_url"]

# 获取工具模块的日志器
logger = get_utils_logger()

def find_url(string: str) -> Optional[str]:
    """
    从文本中提取 URL
    
    参数:
        string: 包含 URL 的文本
        
    返回:
        提取的 URL 或 None (如果未找到)
    """
    try:
        # 如果输入就是一个 URL，直接返回
        if string.startswith(('http://', 'https://')):
            logger.info(f"输入已是URL: {string}")
            return string
            
        # 否则在文本中查找 URL
        # 将中文逗号替换为空格，以便更好地分隔
        tmp = string.replace("，", " ").replace(",", " ")
        
        # 查找 URL
        match = re.search(r"(?P<url>https?://[^\s]+)", tmp)
        if match:
            url = match.group("url")
            # 移除 URL 末尾可能的标点符号
            url = re.sub(r'[.,;:!?)]+$', '', url)
            logger.info(f"从文本中提取到URL: {url}")
            return url
        
        logger.warning(f"在文本中未找到URL: {string}")
        return None
    except Exception as e:
        logger.error(f"提取 URL 时出错: {str(e)}", exc_info=True)
        return None


def get_timestamp(unit: str = "milli"):
    """
    根据给定的单位获取当前时间 (Get the current time based on the given unit)

    Args:
        unit (str): 时间单位，可以是 "milli"、"sec"、"min" 等
            (The time unit, which can be "milli", "sec", "min", etc.)

    Returns:
        int: 根据给定单位的当前时间 (The current time based on the given unit)
    """

    now = datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
    if unit == "milli":
        return int(now.total_seconds() * 1000)
    elif unit == "sec":
        return int(now.total_seconds())
    elif unit == "min":
        return int(now.total_seconds() / 60)
    else:
        raise ValueError("Unsupported time unit")