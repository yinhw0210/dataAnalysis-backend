"""
抖音反检测绕过模块
Douyin Anti-Detection Bypass Module
"""

import asyncio
import random
import time
import json
import hashlib
from typing import Dict, Any, Optional
from src.utils import get_analyze_logger

logger = get_analyze_logger()


class DouyinBypassManager:
    """抖音检测绕过管理器"""
    
    # 真实的移动端设备指纹
    MOBILE_DEVICES = [
        {
            "device_type": "SM-G973F",
            "os_version": "10",
            "resolution": "1080*2340",
            "dpi": "480",
            "user_agent": "com.ss.android.ugc.aweme/290100 (Linux; U; Android 10; zh_CN; SM-G973F; Build/QP1A.190711.020; Cronet/TTNetVersion:b4d74d15 2020-04-23 QuicVersion:0144d358 2020-03-24)"
        },
        {
            "device_type": "iPhone12,1",
            "os_version": "14.7.1",
            "resolution": "828*1792",
            "dpi": "326",
            "user_agent": "Aweme/29.1.0 (iPhone; iOS 14.7.1; Scale/2.00)"
        },
        {
            "device_type": "Pixel 5",
            "os_version": "11",
            "resolution": "1080*2340",
            "dpi": "432",
            "user_agent": "com.ss.android.ugc.aweme/290100 (Linux; U; Android 11; zh_CN; Pixel 5; Build/RQ3A.210905.001; Cronet/TTNetVersion:b4d74d15 2020-04-23 QuicVersion:0144d358 2020-03-24)"
        }
    ]
    
    @classmethod
    async def bypass_web_detection(cls, aweme_id: str, base_headers: Dict[str, str]) -> Optional[Dict]:
        """绕过Web端检测"""
        logger.info("🔄 尝试Web端检测绕过")
        
        # 策略1: 使用iframe嵌入方式
        iframe_result = await cls._try_iframe_method(aweme_id, base_headers)
        if iframe_result:
            return iframe_result
            
        # 策略2: 使用分享链接解析
        share_result = await cls._try_share_link_method(aweme_id, base_headers)
        if share_result:
            return share_result
            
        # 策略3: 使用搜索API
        search_result = await cls._try_search_method(aweme_id, base_headers)
        if search_result:
            return search_result
            
        return None
    
    @classmethod
    async def _try_iframe_method(cls, aweme_id: str, headers: Dict[str, str]) -> Optional[Dict]:
        """尝试iframe嵌入方式"""
        try:
            from src.crawlers.base_crawler import BaseCrawler
            
            # 模拟iframe嵌入请求
            iframe_url = f"https://www.douyin.com/video/{aweme_id}?modeFrom=userPost&secUid="
            
            iframe_headers = headers.copy()
            iframe_headers.update({
                'Referer': 'https://www.douyin.com/',
                'Sec-Fetch-Dest': 'iframe',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Upgrade-Insecure-Requests': '1',
            })
            
            logger.info(f"尝试iframe方式: {iframe_url}")
            
            base_crawler = BaseCrawler(proxies={'http': None, 'https': None}, crawler_headers=iframe_headers)
            async with base_crawler as crawler:
                # 获取页面HTML
                response = await crawler.aclient.get(iframe_url)
                if response.status_code == 200 and response.text:
                    # 从HTML中提取JSON数据
                    json_data = cls._extract_json_from_html(response.text)
                    if json_data:
                        logger.info("✅ iframe方式成功")
                        return json_data
                        
        except Exception as e:
            logger.warning(f"iframe方式失败: {str(e)}")
            
        return None
    
    @classmethod
    async def _try_share_link_method(cls, aweme_id: str, headers: Dict[str, str]) -> Optional[Dict]:
        """尝试分享链接解析方式"""
        try:
            from src.crawlers.base_crawler import BaseCrawler
            
            # 构造分享链接
            share_url = f"https://v.douyin.com/share/video/{aweme_id}/"
            
            share_headers = headers.copy()
            share_headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
            })
            
            logger.info(f"尝试分享链接方式: {share_url}")
            
            base_crawler = BaseCrawler(proxies={'http': None, 'https': None}, crawler_headers=share_headers)
            async with base_crawler as crawler:
                response = await crawler.aclient.get(share_url, follow_redirects=True)
                if response.status_code == 200 and response.text:
                    json_data = cls._extract_json_from_html(response.text)
                    if json_data:
                        logger.info("✅ 分享链接方式成功")
                        return json_data
                        
        except Exception as e:
            logger.warning(f"分享链接方式失败: {str(e)}")
            
        return None
    
    @classmethod
    async def _try_search_method(cls, aweme_id: str, headers: Dict[str, str]) -> Optional[Dict]:
        """尝试搜索API方式"""
        try:
            from src.crawlers.base_crawler import BaseCrawler
            
            # 使用搜索API
            search_url = f"https://www.douyin.com/aweme/v1/web/general/search/single/?keyword={aweme_id}&search_source=video_search"
            
            search_headers = headers.copy()
            search_headers.update({
                'Accept': 'application/json, text/plain, */*',
                'X-Requested-With': 'XMLHttpRequest',
            })
            
            logger.info(f"尝试搜索API方式: {search_url}")
            
            base_crawler = BaseCrawler(proxies={'http': None, 'https': None}, crawler_headers=search_headers)
            async with base_crawler as crawler:
                response = await crawler.fetch_get_json(search_url)
                if response and isinstance(response, dict):
                    logger.info("✅ 搜索API方式成功")
                    return response
                    
        except Exception as e:
            logger.warning(f"搜索API方式失败: {str(e)}")
            
        return None
    
    @classmethod
    def _extract_json_from_html(cls, html_content: str) -> Optional[Dict]:
        """从HTML中提取JSON数据"""
        try:
            import re
            
            # 查找页面中的JSON数据
            patterns = [
                r'window\._ROUTER_DATA\s*=\s*({.+?});',
                r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
                r'self\.__pace_f\.push\(\[function\(\)\{window\._ROUTER_DATA\s*=\s*({.+?})\}',
                r'<script[^>]*>window\._ROUTER_DATA\s*=\s*({.+?})</script>',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.DOTALL)
                for match in matches:
                    try:
                        # 清理JSON字符串
                        json_str = match.strip()
                        if json_str.endswith(';'):
                            json_str = json_str[:-1]
                            
                        data = json.loads(json_str)
                        if data and isinstance(data, dict):
                            # 检查是否包含视频数据
                            if cls._contains_video_data(data):
                                logger.info("✅ 从HTML中提取到有效JSON数据")
                                return data
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            logger.warning(f"从HTML提取JSON失败: {str(e)}")
            
        return None
    
    @classmethod
    def _contains_video_data(cls, data: Dict) -> bool:
        """检查数据是否包含视频信息"""
        try:
            # 递归搜索视频相关字段
            def search_video_fields(obj, depth=0):
                if depth > 10:  # 防止无限递归
                    return False
                    
                if isinstance(obj, dict):
                    # 检查常见的视频字段
                    video_fields = ['aweme_id', 'video', 'aweme_list', 'item_list', 'aweme_detail']
                    for field in video_fields:
                        if field in obj:
                            return True
                    
                    # 递归检查子对象
                    for value in obj.values():
                        if search_video_fields(value, depth + 1):
                            return True
                            
                elif isinstance(obj, list):
                    for item in obj:
                        if search_video_fields(item, depth + 1):
                            return True
                            
                return False
            
            return search_video_fields(data)
            
        except Exception:
            return False
    
    @classmethod
    async def bypass_mobile_detection(cls, aweme_id: str) -> Optional[Dict]:
        """绕过移动端检测"""
        logger.info("🔄 尝试移动端检测绕过")
        
        device = random.choice(cls.MOBILE_DEVICES)
        
        # 构造移动端请求
        mobile_params = {
            'aweme_id': aweme_id,
            'device_platform': 'android' if 'android' in device['user_agent'].lower() else 'iphone',
            'aid': '1128' if 'android' in device['user_agent'].lower() else '1233',
            'version_code': '290100',
            'device_type': device['device_type'],
            'os_version': device['os_version'],
            'resolution': device['resolution'],
            'dpi': device['dpi'],
            'ac': 'wifi',
            'channel': 'App Store' if 'iPhone' in device['device_type'] else 'googleplay',
        }
        
        mobile_headers = {
            'User-Agent': device['user_agent'],
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        
        try:
            from src.crawlers.base_crawler import BaseCrawler
            from urllib.parse import urlencode
            
            mobile_url = f"https://aweme.snssdk.com/aweme/v1/aweme/detail/?{urlencode(mobile_params)}"
            
            logger.info(f"移动端请求: {mobile_url}")
            
            base_crawler = BaseCrawler(proxies={'http': None, 'https': None}, crawler_headers=mobile_headers)
            async with base_crawler as crawler:
                response = await crawler.fetch_get_json(mobile_url)
                if response and isinstance(response, dict):
                    logger.info("✅ 移动端绕过成功")
                    return response
                    
        except Exception as e:
            logger.warning(f"移动端绕过失败: {str(e)}")
            
        return None
    
    @classmethod
    async def emergency_fallback(cls, aweme_id: str) -> Optional[Dict]:
        """紧急备用方案"""
        logger.info("🆘 启用紧急备用方案")
        
        # 返回一个基本的响应结构，表明检测到了视频但无法获取详细信息
        fallback_response = {
            "status_code": 0,
            "aweme_list": [{
                "aweme_id": aweme_id,
                "desc": "视频检测成功，但详细信息获取受限",
                "create_time": int(time.time()),
                "video": {
                    "play_addr": {
                        "url_list": [f"https://www.douyin.com/video/{aweme_id}"]
                    }
                },
                "author": {
                    "nickname": "未知用户",
                    "unique_id": "unknown"
                },
                "statistics": {
                    "digg_count": 0,
                    "comment_count": 0,
                    "share_count": 0
                }
            }]
        }
        
        logger.info("✅ 紧急备用方案激活")
        return fallback_response
