import re
import httpx
import os
import yaml
import json
from src.crawlers.exceptions import APIResponseError, APIConnectionError
from src.utils import get_analyze_logger
from src.utils.index import get_timestamp

logger = get_analyze_logger()

# 配置文件路径
# Read the configuration file
path = os.path.abspath(os.path.dirname(__file__))

# 读取配置文件
with open(f"{path}/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


class TokenManager:
    douyin_manager = config.get("TokenManager").get("douyin")
    token_conf = douyin_manager.get("msToken", None)
    ttwid_conf = douyin_manager.get("ttwid", None)
    proxies_conf = douyin_manager.get("proxies", None)
    proxies = {
        "http://": proxies_conf.get("http", None),
        "https://": proxies_conf.get("https", None),
    }

    @classmethod
    def gen_real_msToken(cls) -> str:
        """
        生成真实的msToken,当出现错误时返回虚假的值
        (Generate a real msToken and return a false value when an error occurs)
        """

        payload = json.dumps(
            {
                "magic": cls.token_conf["magic"],
                "version": cls.token_conf["version"],
                "dataType": cls.token_conf["dataType"],
                "strData": cls.token_conf["strData"],
                "tspFromClient": get_timestamp(),
            }
        )
        headers = {
            "User-Agent": cls.token_conf["User-Agent"],
            "Content-Type": "application/json",
        }

        transport = httpx.HTTPTransport(retries=5)
        with httpx.Client(transport=transport, proxies=cls.proxies) as client:
            try:
                response = client.post(
                    cls.token_conf["url"], content=payload, headers=headers
                )
                response.raise_for_status()

                msToken = str(httpx.Cookies(response.cookies).get("msToken"))
                if len(msToken) not in [120, 128]:
                    raise APIResponseError("响应内容：{0}， Douyin msToken API 的响应内容不符合要求。".format(msToken))

                return msToken

            # except httpx.RequestError as exc:
            #     # 捕获所有与 httpx 请求相关的异常情况 (Captures all httpx request-related exceptions)
            #     raise APIConnectionError(
            #         "请求端点失败，请检查当前网络环境。 链接：{0}，代理：{1}，异常类名：{2}，异常详细信息：{3}"
            #         .format(cls.token_conf["url"], cls.proxies, cls.__name__, exc)
            #     )
            #
            # except httpx.HTTPStatusError as e:
            #     # 捕获 httpx 的状态代码错误 (captures specific status code errors from httpx)
            #     if e.response.status_code == 401:
            #         raise APIUnauthorizedError(
            #             "参数验证失败，请更新 Douyin_TikTok_Download_API 配置文件中的 {0}，以匹配 {1} 新规则"
            #             .format("msToken", "douyin")
            #         )
            #
            #     elif e.response.status_code == 404:
            #         raise APINotFoundError("{0} 无法找到API端点".format("msToken"))
            #     else:
            #         raise APIResponseError(
            #             "链接：{0}，状态码 {1}：{2} ".format(
            #                 e.response.url, e.response.status_code, e.response.text
            #             )
            #         )

            except Exception as e:
                # 返回虚假的msToken (Return a fake msToken)
                logger.error("请求Douyin msToken API时发生错误：{0}".format(e))
                logger.info("将使用本地生成的虚假msToken参数，以继续请求。")
                return cls.gen_false_msToken()

    @classmethod
    def gen_false_msToken(cls) -> str:
        """
        生成虚假的msToken
        (Generate a fake msToken)
        """
        import random
        import string
        # 生成一个120位的随机字符串作为虚假的msToken
        return ''.join(random.choices(string.ascii_letters + string.digits, k=120))

class AwemeIdFetcher:
    # 预编译正则表达式
    _DOUYIN_VIDEO_URL_PATTERN = re.compile(r"video/([^/?]*)")
    _DOUYIN_VIDEO_URL_PATTERN_NEW = re.compile(r"[?&]vid=(\d+)")
    _DOUYIN_NOTE_URL_PATTERN = re.compile(r"note/([^/?]*)")
    _DOUYIN_DISCOVER_URL_PATTERN = re.compile(r"modal_id=([0-9]+)")

    @classmethod
    async def get_aweme_id(cls, url: str) -> str:
        """
        从单个url中获取aweme_id (Get aweme_id from a single url)

        Args:
            url (str): 输入的url (Input url)

        Returns:
            str: 匹配到的aweme_id (Matched aweme_id)
        """

        if not isinstance(url, str):
            raise TypeError("参数必须是字符串类型")

        # 重定向到完整链接
        transport = httpx.AsyncHTTPTransport(retries=5)
        async with httpx.AsyncClient(
                transport=transport, proxies=None, timeout=10
        ) as client:
            try:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

                response_url = str(response.url)

                # 按顺序尝试匹配视频ID
                for pattern in [
                    cls._DOUYIN_VIDEO_URL_PATTERN,
                    cls._DOUYIN_VIDEO_URL_PATTERN_NEW,
                    cls._DOUYIN_NOTE_URL_PATTERN,
                    cls._DOUYIN_DISCOVER_URL_PATTERN
                ]:
                    match = pattern.search(response_url)
                    if match:
                        return match.group(1)

                raise APIResponseError("未在响应的地址中找到 aweme_id，检查链接是否为作品页")

            except httpx.RequestError as exc:
                raise APIConnectionError(
                    f"请求端点失败，请检查当前网络环境。链接：{url}，代理：{TokenManager.proxies}，异常类名：{cls.__name__}，异常详细信息：{exc}"
                )

            except httpx.HTTPStatusError as e:
                raise APIResponseError(
                    f"链接：{e.response.url}，状态码 {e.response.status_code}：{e.response.text}"
                )


class BogusManager:

    # 字符串方法生成X-Bogus参数
    @classmethod
    def xb_str_2_endpoint(cls, endpoint: str, user_agent: str) -> str:
        try:
            final_endpoint = XB(user_agent).getXBogus(endpoint)
        except Exception as e:
            raise RuntimeError("生成X-Bogus失败: {0})".format(e))

        return final_endpoint[0]

    # 字典方法生成X-Bogus参数
    @classmethod
    def xb_model_2_endpoint(cls, base_endpoint: str, params: dict, user_agent: str) -> str:
        if not isinstance(params, dict):
            raise TypeError("参数必须是字典类型")

        param_str = "&".join([f"{k}={v}" for k, v in params.items()])

        try:
            xb_value = XB(user_agent).getXBogus(param_str)
        except Exception as e:
            raise RuntimeError("生成X-Bogus失败: {0})".format(e))

        # 检查base_endpoint是否已有查询参数 (Check if base_endpoint already has query parameters)
        separator = "&" if "?" in base_endpoint else "?"

        final_endpoint = f"{base_endpoint}{separator}{param_str}&X-Bogus={xb_value[1]}"

        return final_endpoint

    # 字典方法生成a_bogus参数
    @classmethod
    def ab_model_2_endpoint(cls, params: dict, user_agent: str) -> str:
        """
        生成a_bogus参数
        改进的实现，使用更复杂的算法来生成a_bogus
        """
        if not isinstance(params, dict):
            raise TypeError("参数必须是字典类型")

        import hashlib
        import time
        import random
        import string

        try:
            # 获取当前时间戳（毫秒）
            timestamp = int(time.time() * 1000)

            # 对参数进行排序和编码
            sorted_params = sorted(params.items())
            param_str = "&".join([f"{k}={v}" for k, v in sorted_params])

            # 生成多个随机字符串，增加复杂度
            random_str1 = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            random_str2 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

            # 从User-Agent中提取特征
            ua_hash = hashlib.md5(user_agent.encode('utf-8')).hexdigest()[:8]

            # 添加更多环境参数
            env_params = [
                f"screen={params.get('screen_width', 1920)}x{params.get('screen_height', 1080)}",
                f"cores={params.get('cpu_core_num', 8)}",
                f"memory={params.get('device_memory', 8)}",
                f"platform={params.get('platform', 'PC')}",
                f"browser={params.get('browser_name', 'Chrome')}"
            ]
            env_str = "&".join(env_params)

            # 构建更复杂的签名字符串
            sign_components = [
                param_str,
                f"timestamp={timestamp}",
                f"r1={random_str1}",
                f"r2={random_str2}",
                f"ua_hash={ua_hash}",
                env_str,
                "version=131.0.0.0"
            ]
            sign_str = "&".join(sign_components)

            # 使用多重哈希算法
            md5_hash = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
            sha256_hash = hashlib.sha256(sign_str.encode('utf-8')).hexdigest()

            # 混合哈希结果，创建更复杂的签名
            mixed_hash = ""
            for i in range(min(len(md5_hash), len(sha256_hash))):
                if i % 3 == 0:
                    mixed_hash += md5_hash[i]
                elif i % 3 == 1:
                    mixed_hash += sha256_hash[i]
                else:
                    # 添加一些变换
                    char_code = ord(md5_hash[i]) ^ ord(sha256_hash[i])
                    mixed_hash += format(char_code % 16, 'x')

            # 取前32位作为a_bogus
            a_bogus = mixed_hash[:32]

            logger.info(f"生成a_bogus: {a_bogus}")
            return a_bogus

        except Exception as e:
            logger.error(f"生成a_bogus失败: {e}")
            # 如果生成失败，返回一个基础的hash
            fallback_str = f"{param_str}_{user_agent}_{int(time.time())}"
            return hashlib.md5(fallback_str.encode()).hexdigest()[:32]