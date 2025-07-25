from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from src.app.kuaishou.index import Kuaishou
from src.app.douyin.index import Douyin
from src.app.weibo.index import Weibo
from src.utils import config, get_analyze_logger,get_utils_logger
from src.app.xiaohongshu.index import Xiaohongshu
from src.routes.youtube import router as youtube_router

# 获取应用日志器
logger = get_analyze_logger()
utils_logger = get_utils_logger()


class AnalyzeParams(BaseModel):
    url: str
    type: Optional[str] = "png"
    format: Optional[str] = "json"


# 创建路由器
router = APIRouter(
    prefix="/analyze",
    tags=["analyze"],
    responses={404: {"description": "Not found"}},
)

# 包含YouTube路由
router.include_router(youtube_router)

# 无前缀的POST端点
@router.post("")
async def process_analyze(params: AnalyzeParams,request: Request):
    # 打印ip地址和请求参数
    logger.info(f"ip地址: {request.client.host}, 请求参数: {params}")
    try:
        url = params.url
        app_type = ""
        # 判断url是否包含小红书或抖音
        if any(keyword in url for keyword in config.APP_TYPE_KEYWORD["xiaohongshu"]):
            app_type = "xiaohongshu"
        elif any(keyword in url for keyword in config.APP_TYPE_KEYWORD["douyin"]):
            app_type = "douyin"
        elif any(keyword in url for keyword in config.APP_TYPE_KEYWORD["kuaishou"]):
            app_type = "kuaishou"
        elif any(keyword in url for keyword in config.APP_TYPE_KEYWORD["weibo"]):
            app_type = "weibo"
        else:
            from src.utils.response import Response
            return Response.error("不支持的URL")
        
        
        # 根据app_type选择对应的模块
        if app_type == 'xiaohongshu':
            from src.app.xiaohongshu.index import Xiaohongshu
            xiaohongshu = Xiaohongshu(url, params.type)
            return xiaohongshu.to_dict()
        elif app_type == 'douyin':
            from src.app.douyin.index import Douyin
            douyin = Douyin(url, params.type)
            return douyin.to_dict()
        elif app_type == 'kuaishou':
            from src.app.kuaishou.index import Kuaishou
            kuaishou = Kuaishou(url, params.type)
            return kuaishou.to_dict()
        elif app_type == 'weibo':
            from src.app.weibo.index import Weibo
            weibo = Weibo(url, params.type)
            return weibo.to_dict()
        else:
            from src.utils.response import Response
            return Response.error("请联系客服！")
    
    except Exception as e:
        logger.error(f"处理聚合数据出错: {url}", exc_info=True)
        logger.error(f"处理聚合数据出错: {str(e)}", exc_info=True)
        from src.utils.response import Response
        raise HTTPException(status_code=500, detail=Response.error(str(e)))

# 小红书
@router.post("/xiaohongshu")
async def process_xiaohongshu(params: AnalyzeParams):
    """
    处理小红书 URL 并返回数据
    
    参数:
    - url: 小红书链接
    - type: 图片类型，支持 "png" 或 "webp"
    - format: 返回格式，支持 "json" 或 "html"
    """
    logger.info(f"处理小红书URL (POST): {params.url}")
    try:
        xiaohongshu = Xiaohongshu(params.url, params.type)
        
        if params.format.lower() == "html":
            # 返回 HTML 内容
            from src.utils.response import Response
            return Response.success(xiaohongshu.html, "获取成功")
        else:
            # 返回结构化数据
            return xiaohongshu.to_dict()
    except Exception as e:
        logger.error(f"处理小红书URL出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
# 抖音
@router.post("/douyin")
async def process_douyin(params: AnalyzeParams):
    """
    处理抖音 URL 并返回数据
    
    参数:
    - url: 抖音链接
    - type: 图片类型，支持 "png" 或 "webp"
    - format: 返回格式，支持 "json" 或 "html"
    """
    logger.info(f"处理抖音URL (POST): {params.url}")
    try:
        douyin = Douyin(params.url, params.type)
        
        if params.format.lower() == "html":
            # 返回 HTML 内容
            from src.utils.response import Response
            return Response.success(douyin.html, "获取成功")
        else:
            # 返回结构化数据
            return douyin.to_dict()
    except Exception as e:
        logger.error(f"处理抖音URL出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# 快手
@router.post("/kuaishou")
async def process_kuaishou(params: AnalyzeParams):
    """
    处理快手 URL 并返回数据
    
    参数:
    - url: 快手链接
    - type: 图片类型，支持 "png" 或 "webp"
    - format: 返回格式，支持 "json" 或 "html"
    """
    logger.info(f"处理快手URL (POST): {params.url}")
    try:
        kuaishou = Kuaishou(params.url, params.type)
        
        if params.format.lower() == "html":
            # 返回 HTML 内容
            from src.utils.response import Response
            return Response.success(kuaishou.html, "获取成功")
        else:
            # 返回结构化数据
            return kuaishou.to_dict()
    except Exception as e:
        logger.error(f"处理快手URL出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
# 微博
@router.post("/weibo")
async def process_weibo(params: AnalyzeParams):
    """
    处理微博 URL 并返回数据
    
    参数:
    - url: 微博链接
    - type: 图片类型，支持 "png" 或 "webp"
    - format: 返回格式，支持 "json" 或 "html"
    """
    logger.info(f"处理微博URL (POST): {params.url}")
    try:
        weibo = Weibo(params.url)
        
        if params.format.lower() == "html":
            # 返回 HTML 内容
            from src.utils.response import Response
            return Response.success(weibo.html, "获取成功")
        else:
            # 返回结构化数据
            return weibo.to_dict()
    except Exception as e:
        logger.error(f"处理抖音URL出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))