from pydantic import BaseModel

# 导入异常类
from .exceptions import (
    APIError,
    APIConnectionError,
    APIResponseError,
    APITimeoutError,
    APIUnavailableError,
    APIUnauthorizedError,
    APINotFoundError,
    APIRateLimitError,
    APIRetryExhaustedError,
)

# Base Model
class BaseRequestModel(BaseModel):
    device_platform: str = "webapp"
    aid: str = "6383"
    channel: str = "channel_pc_web"
    pc_client_type: int = 1
    version_code: str = "290100"
    version_name: str = "29.1.0"
    cookie_enabled: str = "true"
    screen_width: int = 1920
    screen_height: int = 1080
    browser_language: str = "zh-CN"
    browser_platform: str = "Win32"
    browser_name: str = "Chrome"
    browser_version: str = "131.0.0.0"
    browser_online: str = "true"
    engine_name: str = "Blink"
    engine_version: str = "131.0.0.0"
    os_name: str = "Windows"
    os_version: str = "10"
    cpu_core_num: int = 12
    device_memory: int = 8
    platform: str = "PC"
    downlink: str = "10"
    effective_type: str = "4g"
    from_user_page: str = "1"
    locate_query: str = "false"
    need_time_list: str = "1"
    pc_libra_divert: str = "Windows"
    publish_video_strategy_type: str = "2"
    round_trip_time: str = "0"
    show_live_replay_strategy: str = "1"
    time_list_query: str = "0"
    whale_cut_token: str = ""
    update_version_code: str = "170400"
    # 延迟导入 TokenManager 以避免循环导入
    msToken: str = ""

    def __init__(self, **data):
        # 在初始化时动态获取 msToken
        if 'msToken' not in data or not data['msToken']:
            from src.crawlers.douyin.util import TokenManager
            msToken = TokenManager.gen_real_msToken()
            print(f"msToken: {msToken}")
            data['msToken'] = msToken
        super().__init__(**data)

class PostDetail(BaseRequestModel):
    aweme_id: str