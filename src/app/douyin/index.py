import json
import os
import yaml
import httpx
from src.crawlers.base_crawler import BaseCrawler
from src.crawlers.douyin.endpoints import DouyinAPIEndpoints
from src.crawlers.douyin.util import AwemeIdFetcher, BogusManager
from src.crawlers.util import PostDetail
from src.crawlers.exceptions import APIResponseError
from src.utils import get_analyze_logger, config
from src.utils.index import find_url
from src.utils.response import Response
from urllib.parse import urlencode
from pathlib import Path


logger = get_analyze_logger()

# 配置文件路径
# Read the configuration file
path = Path(__file__).parent.parent.parent / "crawlers" / "douyin" / "config.yaml"

# 读取配置文件
with open(f"{path}", "r", encoding="utf-8") as f:
    douyinConfig = yaml.safe_load(f)
    logger.info(f"douyinConfig: {douyinConfig}")


class Douyin:
    def __init__(self, text, type):
        self.url = find_url(text)
        self.text = text
        self.type = type
        self.aweme_id = None
        self.video_data = None
        # 初始化时不执行异步操作，而是在需要时调用

    async def initialize(self):
        """异步初始化方法"""
        try:
            self.aweme_id = await AwemeIdFetcher.get_aweme_id(self.url)
            logger.info(f"aweme_id: {self.aweme_id}")
            self.video_data = await self.fetch_one_video(self.aweme_id)
            logger.info(f"video_data: {self.video_data}")
        except Exception as e:
            logger.error(f"初始化抖音数据时出错: {str(e)}", exc_info=True)
            raise

    # 从配置文件中获取抖音的请求头
    async def get_douyin_headers(self):
        douyin_config = douyinConfig["TokenManager"]["douyin"]
        kwargs = {
            "headers": {
                "Accept-Language": douyin_config["headers"]["Accept-Language"],
                "User-Agent": douyin_config["headers"]["User-Agent"],
                "Referer": douyin_config["headers"]["Referer"],
                "Cookie": douyin_config["headers"]["Cookie"],
            },
            "proxies": {
                "http://": douyin_config["proxies"]["http"],
                "https://": douyin_config["proxies"]["https"],
            },
        }
        return kwargs

     # 获取单个作品数据
    async def fetch_one_video(self, aweme_id: str):
        # 导入必要模块
        import asyncio
        from src.crawlers.exceptions import APIResponseError

        # 尝试多种策略获取数据
        strategies = [
            self._strategy_web_api,
            self._strategy_bypass_detection,
            self._strategy_mobile_api,
            self._strategy_alternative_endpoint,
            self._strategy_emergency_fallback
        ]

        for i, strategy in enumerate(strategies, 1):
            try:
                logger.info(f"🔄 尝试策略 {i}/{len(strategies)}: {strategy.__name__}")
                result = await strategy(aweme_id)
                if result and self._is_valid_response(result):
                    logger.info(f"✅ 策略 {i} 成功获取数据")
                    return result
                else:
                    logger.warning(f"❌ 策略 {i} 返回无效数据")
            except Exception as e:
                logger.error(f"❌ 策略 {i} 执行失败: {str(e)}")

            # 策略间延迟
            if i < len(strategies):
                await asyncio.sleep(2)

        logger.error("🚫 所有策略都失败了")
        raise APIResponseError("所有获取策略都失败")

    def _is_valid_response(self, response):
        """验证响应是否有效"""
        if not response:
            return False
        if isinstance(response, dict):
            return len(str(response)) > 100  # 简单检查数据量
        return True

    async def _strategy_web_api(self, aweme_id: str):
        """策略1: 标准Web API"""
        import asyncio
        from src.crawlers.douyin.anti_detection import AntiDetectionManager, CookieManager

        # 获取抖音的实时Cookie
        kwargs = await self.get_douyin_headers()

        # 验证Cookie有效性
        if not CookieManager.validate_cookie_freshness(kwargs["headers"].get("Cookie", "")):
            logger.warning("Cookie可能已过期，建议更新")

        # 使用反检测管理器生成真实的参数
        base_params = PostDetail(aweme_id=aweme_id).model_dump()
        realistic_params = AntiDetectionManager.generate_realistic_params(base_params)

        params = PostDetail(aweme_id=aweme_id, **{k: v for k, v in realistic_params.items() if k != 'aweme_id'})
        params_dict = params.model_dump()

        # 生成a_bogus签名
        a_bogus = BogusManager.ab_model_2_endpoint(params_dict, kwargs["headers"]["User-Agent"])

        # 构建完整的请求URL
        endpoint = f"{DouyinAPIEndpoints.POST_DETAIL}?{urlencode(params_dict)}&a_bogus={a_bogus}"

        logger.info("=" * 80)
        logger.info("抖音Web API请求详细信息:")
        logger.info(f"完整请求URL: {endpoint}")
        logger.info(f"a_bogus签名: {a_bogus}")
        logger.info("=" * 80)

        # 使用反检测管理器添加智能延迟
        delay = AntiDetectionManager.add_timing_jitter()
        await asyncio.sleep(delay)

        # 使用反检测管理器生成真实的请求头
        enhanced_headers = AntiDetectionManager.generate_realistic_headers(kwargs["headers"])

        # 创建一个基础爬虫
        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=enhanced_headers)
        async with base_crawler as crawler:
            response = await crawler.fetch_get_json(endpoint)
            return response

    async def _strategy_mobile_api(self, aweme_id: str):
        """策略2: 移动端API模拟"""
        import asyncio
        import time

        logger.info("🔄 尝试移动端API策略")

        # 获取移动端配置
        kwargs = await self.get_douyin_headers()

        # 修改为移动端参数
        mobile_params = {
            'aweme_id': aweme_id,
            'device_platform': 'android',
            'aid': '1128',
            'version_code': '290100',
            'version_name': '29.1.0',
            'device_type': 'SM-G973F',
            'os_version': '10',
            'resolution': '1080*2340',
            'dpi': '480',
            'update_version_code': '290100',
            'ac': 'wifi',
            'channel': 'googleplay',
            'app_name': 'aweme',
            'version_code': '290100',
            'manifest_version_code': '290100',
            'app_type': 'normal'
        }

        # 移动端User-Agent
        mobile_headers = kwargs["headers"].copy()
        mobile_headers.update({
            'User-Agent': 'com.ss.android.ugc.aweme/290100 (Linux; U; Android 10; zh_CN; SM-G973F; Build/QP1A.190711.020; Cronet/TTNetVersion:b4d74d15 2020-04-23 QuicVersion:0144d358 2020-03-24)',
            'X-Khronos': str(int(time.time())),
            'X-Gorgon': self._generate_gorgon(),
            'X-Ladon': self._generate_ladon(),
        })

        # 构建移动端API URL
        mobile_endpoint = f"https://aweme.snssdk.com/aweme/v1/aweme/detail/?{urlencode(mobile_params)}"

        logger.info(f"移动端API URL: {mobile_endpoint}")

        await asyncio.sleep(1)

        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=mobile_headers)
        async with base_crawler as crawler:
            response = await crawler.fetch_get_json(mobile_endpoint)
            return response

    async def _strategy_alternative_endpoint(self, aweme_id: str):
        """策略3: 备用端点"""
        import asyncio

        logger.info("🔄 尝试备用端点策略")

        kwargs = await self.get_douyin_headers()

        # 尝试不同的端点
        alternative_endpoints = [
            f"https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={aweme_id}&aid=1128&version_name=23.5.0&device_platform=webapp&os=pc",
            f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={aweme_id}",
            f"https://www.douyin.com/aweme/v1/web/aweme/post/?aweme_id={aweme_id}"
        ]

        for endpoint in alternative_endpoints:
            try:
                logger.info(f"尝试端点: {endpoint}")

                # 简化的请求头
                simple_headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'Referer': 'https://www.douyin.com/',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cookie': kwargs["headers"].get("Cookie", "")
                }

                await asyncio.sleep(1)

                base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=simple_headers)
                async with base_crawler as crawler:
                    response = await crawler.fetch_get_json(endpoint)
                    if response and len(str(response)) > 50:
                        logger.info(f"✅ 备用端点成功: {endpoint}")
                        return response

            except Exception as e:
                logger.warning(f"备用端点失败 {endpoint}: {str(e)}")
                continue

        return None

    async def _strategy_bypass_detection(self, aweme_id: str):
        """策略2: 检测绕过"""
        from src.crawlers.douyin.bypass_detection import DouyinBypassManager

        logger.info("🔄 尝试检测绕过策略")

        kwargs = await self.get_douyin_headers()

        # 尝试Web端绕过
        result = await DouyinBypassManager.bypass_web_detection(aweme_id, kwargs["headers"])
        if result:
            return result

        # 尝试移动端绕过
        result = await DouyinBypassManager.bypass_mobile_detection(aweme_id)
        if result:
            return result

        return None

    async def _strategy_emergency_fallback(self, aweme_id: str):
        """策略5: 紧急备用方案"""
        from src.crawlers.douyin.bypass_detection import DouyinBypassManager

        logger.info("🆘 启用紧急备用策略")

        # 使用紧急备用方案
        result = await DouyinBypassManager.emergency_fallback(aweme_id)
        return result

    def _generate_gorgon(self):
        """生成X-Gorgon头"""
        import hashlib
        import time
        timestamp = str(int(time.time()))
        return hashlib.md5(f"gorgon_{timestamp}".encode()).hexdigest()[:8]

    def _generate_ladon(self):
        """生成X-Ladon头"""
        import hashlib
        import time
        timestamp = str(int(time.time()))
        return hashlib.md5(f"ladon_{timestamp}".encode()).hexdigest()[:8]

    def to_dict(self):
        """将对象转换为字典，用于 API 返回"""
        try:
            result = {
                "aweme_id": self.aweme_id,
                "video_data": self.video_data,
                # "url": self.url,
                # "final_url": "",
                # "title": self.title,
                # "description": self.description,
                # "image_list": self.image_list,
                # "video": self.video,
                # "app_type": "douyin",
            }
            return Response.success(result, "获取成功")
        except Exception as e:
            logger.error(f"抖音转换为字典时出错: {str(e)}", exc_info=True)
            return Response.error("获取失败")
