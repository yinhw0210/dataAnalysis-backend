"""
豆包去水印 API 路由
独立模块，优先级最高
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io

from src.app.doubao.extractor import extract_doubao_images, download_doubao_image
from src.utils import get_app_logger
from src.utils.response import Response

logger = get_app_logger()


class DoubaoExtractRequest(BaseModel):
    """豆包提取请求"""
    url: str


class DoubaoDownloadRequest(BaseModel):
    """豆包图片下载请求"""
    url: str
    filename: Optional[str] = None


# 创建独立路由器
router = APIRouter(
    prefix="/doubao",
    tags=["doubao"],
    responses={404: {"description": "Not found"}},
)


@router.post("/extract")
async def extract_images(params: DoubaoExtractRequest):
    """
    提取豆包分享链接中的无水印原图
    
    参数:
    - url: 豆包分享链接 (如 https://www.doubao.com/thread/xxx)
    
    返回:
    - images: 图片列表，包含 id, original_url, width, height, prompt 等信息
    """
    logger.info(f"[Doubao API] 提取请求: {params.url}")
    
    # 验证 URL
    if not params.url or 'doubao.com' not in params.url:
        return Response.error("请提供有效的豆包分享链接")
    
    try:
        result = await extract_doubao_images(params.url)
        
        if result['success']:
            return Response.success({
                'url': result['url'],
                'image_count': result['image_count'],
                'images': result['images']
            }, "提取成功")
        else:
            return Response.error(result.get('error', '提取失败'))
            
    except Exception as e:
        logger.error(f"[Doubao API] 提取异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download")
async def download_image(params: DoubaoDownloadRequest):
    """
    下载豆包图片（返回 base64）
    
    参数:
    - url: 图片 URL
    - filename: 可选的文件名
    
    返回:
    - image_base64: 图片的 base64 编码
    """
    logger.info(f"[Doubao API] 下载请求: {params.url}")
    
    try:
        import base64
        image_data = await download_doubao_image(params.url)
        
        if image_data:
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            return Response.success({
                'image_base64': image_base64,
                'size': len(image_data),
                'filename': params.filename or 'doubao_image.png'
            }, "下载成功")
        else:
            return Response.error("下载失败")
            
    except Exception as e:
        logger.error(f"[Doubao API] 下载异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download_stream")
async def download_image_stream(params: DoubaoDownloadRequest):
    """
    下载豆包图片（返回文件流）
    
    参数:
    - url: 图片 URL
    - filename: 可选的文件名
    
    返回:
    - 图片文件流
    """
    logger.info(f"[Doubao API] 流式下载请求: {params.url}")
    
    try:
        image_data = await download_doubao_image(params.url)
        
        if image_data:
            filename = params.filename or 'doubao_image.png'
            return StreamingResponse(
                io.BytesIO(image_data),
                media_type="image/png",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )
        else:
            raise HTTPException(status_code=404, detail="下载失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Doubao API] 流式下载异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
