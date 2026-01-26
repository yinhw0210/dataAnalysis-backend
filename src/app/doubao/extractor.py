"""
豆包分享链接原图提取器
使用 curl_cffi 模拟浏览器请求提取无水印原图
"""

import os
import re
from typing import List, Dict, Optional
from curl_cffi import requests

from src.utils import get_app_logger

logger = get_app_logger()

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DOWNLOAD_DIR = os.path.join(ROOT_DIR, 'storage', 'doubao_downloads')


class DoubaoExtractor:
    """豆包图片提取器 - 使用 curl_cffi"""
    
    def __init__(self):
        self.session = None
    
    def _get_session(self):
        """获取请求会话"""
        if self.session is None:
            self.session = requests.Session(impersonate="chrome")
        return self.session
    
    async def extract_images(self, share_url: str) -> Dict:
        """
        从分享链接提取原图信息
        
        Args:
            share_url: 豆包分享链接
            
        Returns:
            包含图片信息的字典
        """
        logger.info(f"[Doubao] 开始提取: {share_url}")
        
        try:
            session = self._get_session()
            
            # 设置请求头
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Referer': 'https://www.doubao.com/',
            }
            
            # 发送请求
            response = session.get(share_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            html = response.text
            logger.info(f"[Doubao] 页面长度: {len(html)}")
            
            # 提取图片
            images = self._extract_images_from_html(html)
            
            return {
                'success': True,
                'url': share_url,
                'image_count': len(images),
                'images': images
            }
            
        except Exception as e:
            logger.error(f"[Doubao] 提取失败: {e}")
            return {
                'success': False,
                'url': share_url,
                'error': str(e),
                'images': []
            }
    
    def _extract_images_from_html(self, html: str) -> List[Dict]:
        """从 HTML 中提取图片信息"""
        images = []
        seen_ids = set()
        
        # 预处理 HTML - 处理多层转义
        normalized = html
        # 处理多层 Unicode 转义
        for _ in range(3):
            normalized = normalized.replace('\\u002F', '/').replace('\\u0026', '&')
            normalized = normalized.replace('\\\\u002F', '/').replace('\\\\u0026', '&')
            normalized = normalized.replace('\\/', '/')
            normalized = normalized.replace('&amp;', '&')
        
        # 只匹配 rc_gen_image 路径的原图 URL (排除头像等其他图片)
        pattern = r'(https://[^"\']+?/rc_gen_image/([a-f0-9]{32})\.jpeg~tplv-a9rns2rl98-image_raw_b\.png[^"\']*?)'
        matches = re.findall(pattern, normalized)
        
        logger.info(f"[Doubao] 找到 {len(matches)} 个原图 URL")
        
        for url, image_id in matches:
            # 去重
            if image_id in seen_ids:
                continue
            seen_ids.add(image_id)
            
            # 清理 URL
            url = self._decode_url(url)
            
            # 提取尺寸信息
            width = 2730
            height = 1535
            
            # 尝试从 HTML 中提取实际尺寸
            size_pattern = rf'{image_id}[^}}]*?width[^:]*?:\s*(\d+)[^}}]*?height[^:]*?:\s*(\d+)'
            size_match = re.search(size_pattern, normalized)
            if size_match:
                width = int(size_match.group(1))
                height = int(size_match.group(2))
            
            images.append({
                'id': image_id,
                'original_url': url,
                'width': width,
                'height': height,
            })
        
        # 提取提示词
        self._extract_prompts(normalized, images)
        
        logger.info(f"[Doubao] 提取到 {len(images)} 张图片")
        return images
    
    def _extract_prompts(self, html: str, images: List[Dict]):
        """提取图片的生成提示词"""
        for img in images:
            if not img['id']:
                continue
            
            # 查找 gen_params 中的 prompt
            pattern = rf'{img["id"]}[^}}]*?gen_params[^}}]*?prompt[^:]*?:\s*["\']([^"\']+?)["\']'
            match = re.search(pattern, html, re.DOTALL)
            
            if match:
                prompt = match.group(1)
                # 清理转义字符
                prompt = prompt.replace('\\n', '\n')
                prompt = prompt.replace('\\u002F', '/')
                prompt = prompt.replace('&quot;', '"')
                prompt = prompt.replace('&amp;', '&')
                img['prompt'] = prompt[:500]  # 限制长度
    
    def _decode_url(self, url: str) -> str:
        """解码 URL"""
        if not url:
            return ''
        while '\\\\' in url:
            url = url.replace('\\\\', '\\')
        url = url.replace('\\u002F', '/')
        url = url.replace('\\u0026', '&')
        url = url.replace('\\/', '/')
        url = url.replace('\\&', '&')
        url = url.rstrip('\\')
        return url
    
    async def download_image(self, url: str) -> Optional[bytes]:
        """
        下载图片并返回二进制数据
        
        Args:
            url: 图片 URL
            
        Returns:
            图片二进制数据，失败返回 None
        """
        try:
            session = self._get_session()
            
            headers = {
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://www.doubao.com/',
            }
            
            response = session.get(url, headers=headers, timeout=60)
            response.raise_for_status()
            
            logger.info(f"[Doubao] 下载成功: {len(response.content)} bytes")
            return response.content
            
        except Exception as e:
            logger.error(f"[Doubao] 下载异常: {e}")
            return None
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()
            self.session = None


# 全局提取器实例
_extractor: Optional[DoubaoExtractor] = None


async def get_extractor() -> DoubaoExtractor:
    """获取全局提取器实例"""
    global _extractor
    if _extractor is None:
        _extractor = DoubaoExtractor()
    return _extractor


async def extract_doubao_images(share_url: str) -> Dict:
    """
    提取豆包分享链接中的无水印原图
    
    Args:
        share_url: 豆包分享链接
        
    Returns:
        包含图片信息的字典
    """
    extractor = await get_extractor()
    return await extractor.extract_images(share_url)


async def download_doubao_image(url: str) -> Optional[bytes]:
    """
    下载豆包图片
    
    Args:
        url: 图片 URL
        
    Returns:
        图片二进制数据
    """
    extractor = await get_extractor()
    return await extractor.download_image(url)
