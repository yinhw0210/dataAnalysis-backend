"""
抖音反检测增强模块
Enhanced Anti-Detection Module for Douyin
"""

import random
import time
import hashlib
import json
from typing import Dict, Any
from src.utils import get_analyze_logger

logger = get_analyze_logger()


class AntiDetectionManager:
    """抖音反检测管理器"""
    
    # 真实的浏览器指纹池
    BROWSER_FINGERPRINTS = [
        {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec_ch_ua_platform": '"Windows"',
            "screen_width": 1920,
            "screen_height": 1080,
            "cpu_cores": 8,
            "memory": 8
        },
        {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            "sec_ch_ua": '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
            "sec_ch_ua_platform": '"Windows"',
            "screen_width": 1366,
            "screen_height": 768,
            "cpu_cores": 4,
            "memory": 8
        },
        {
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec_ch_ua_platform": '"macOS"',
            "screen_width": 1440,
            "screen_height": 900,
            "cpu_cores": 8,
            "memory": 16
        }
    ]
    
    @classmethod
    def get_random_fingerprint(cls) -> Dict[str, Any]:
        """获取随机浏览器指纹"""
        return random.choice(cls.BROWSER_FINGERPRINTS).copy()
    
    @classmethod
    def generate_realistic_headers(cls, base_headers: Dict[str, str]) -> Dict[str, str]:
        """生成更真实的请求头"""
        fingerprint = cls.get_random_fingerprint()
        
        enhanced_headers = base_headers.copy()
        enhanced_headers.update({
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Ch-Ua": fingerprint["sec_ch_ua"],
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": fingerprint["sec_ch_ua_platform"],
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": fingerprint["user_agent"],
            # 添加一些随机的自定义头
            "X-Client-Version": f"29.{random.randint(1, 9)}.0",
            "X-Tt-Env": "prod",
        })
        
        return enhanced_headers
    
    @classmethod
    def generate_realistic_params(cls, base_params: Dict[str, Any]) -> Dict[str, Any]:
        """生成更真实的请求参数"""
        fingerprint = cls.get_random_fingerprint()
        
        # 基于指纹更新参数
        realistic_params = base_params.copy()
        realistic_params.update({
            "screen_width": fingerprint["screen_width"],
            "screen_height": fingerprint["screen_height"],
            "cpu_core_num": fingerprint["cpu_cores"],
            "device_memory": fingerprint["memory"],
            "round_trip_time": str(random.randint(20, 150)),
            "downlink": str(random.choice([10, 50, 100])),
            "effective_type": random.choice(["4g", "wifi"]),
            # 添加一些时间相关的参数
            "browser_online": "true",
            "cookie_enabled": "true",
            # 随机化版本号
            "version_code": f"29{random.randint(1000, 9999)}",
            "update_version_code": f"17{random.randint(1000, 9999)}",
        })
        
        return realistic_params
    
    @classmethod
    def add_timing_jitter(cls) -> float:
        """添加时间抖动，模拟真实用户行为"""
        # 模拟用户思考时间和网络延迟
        base_delay = random.uniform(0.5, 2.0)  # 基础延迟
        network_jitter = random.uniform(0.1, 0.5)  # 网络抖动
        user_behavior = random.uniform(0.2, 1.0)  # 用户行为延迟
        
        total_delay = base_delay + network_jitter + user_behavior
        logger.info(f"添加请求延迟: {total_delay:.2f}秒")
        return total_delay
    
    @classmethod
    def generate_session_consistency(cls) -> Dict[str, str]:
        """生成会话一致性参数"""
        session_id = hashlib.md5(f"{time.time()}_{random.randint(1000, 9999)}".encode()).hexdigest()[:16]
        
        return {
            "session_id": session_id,
            "request_id": f"req_{int(time.time() * 1000)}_{random.randint(100, 999)}",
            "trace_id": f"trace_{session_id}_{random.randint(10000, 99999)}"
        }
    
    @classmethod
    def validate_response(cls, response_data: Any) -> bool:
        """验证响应数据是否有效"""
        if not response_data:
            logger.warning("响应数据为空")
            return False
            
        if isinstance(response_data, dict):
            # 检查是否包含错误信息
            if "status_code" in response_data and response_data["status_code"] != 0:
                logger.warning(f"响应包含错误状态码: {response_data.get('status_code')}")
                return False
                
            # 检查是否包含有效的视频数据
            if "aweme_list" in response_data:
                aweme_list = response_data["aweme_list"]
                if not aweme_list or len(aweme_list) == 0:
                    logger.warning("aweme_list为空")
                    return False
                return True
                
        return True
    
    @classmethod
    def log_detection_attempt(cls, url: str, headers: Dict[str, str], params: Dict[str, Any]):
        """记录检测尝试的详细信息"""
        logger.info("=" * 80)
        logger.info("抖音反检测请求详情:")
        logger.info(f"请求URL: {url}")
        logger.info(f"User-Agent: {headers.get('User-Agent', 'N/A')}")
        logger.info(f"屏幕分辨率: {params.get('screen_width')}x{params.get('screen_height')}")
        logger.info(f"CPU核心数: {params.get('cpu_core_num')}")
        logger.info(f"内存大小: {params.get('device_memory')}GB")
        logger.info(f"网络类型: {params.get('effective_type')}")
        logger.info(f"往返时间: {params.get('round_trip_time')}ms")
        logger.info("=" * 80)


class CookieManager:
    """Cookie管理器"""
    
    @classmethod
    def refresh_critical_cookies(cls, current_cookies: str) -> str:
        """刷新关键的Cookie参数"""
        # 这里可以实现Cookie的智能刷新逻辑
        # 目前返回原始Cookie，但可以在未来添加更复杂的逻辑
        logger.info("Cookie刷新检查完成")
        return current_cookies
    
    @classmethod
    def validate_cookie_freshness(cls, cookies: str) -> bool:
        """验证Cookie的新鲜度"""
        # 简单的Cookie有效性检查
        if not cookies or len(cookies) < 100:
            logger.warning("Cookie过短，可能无效")
            return False
            
        # 检查关键Cookie字段
        required_fields = ["sessionid", "sid_tt", "uid_tt"]
        for field in required_fields:
            if field not in cookies:
                logger.warning(f"缺少关键Cookie字段: {field}")
                return False
                
        logger.info("Cookie验证通过")
        return True
