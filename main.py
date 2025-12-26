from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import os
import sys
import logging

class AnalyzeParams(BaseModel):
    url: str
    type: Optional[str] = "png"
    format: Optional[str] = "json"

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入配置和日志模块
from src.utils import get_app_logger, config, get_environment, EnvType

# 获取应用日志器
logger = get_app_logger()

# 根据当前环境记录信息
current_env = get_environment()
logger.info(f"应用启动于 {current_env} 环境")

# Create FastAPI application
app = FastAPI(
    title=config.API_TITLE,
    description=config.API_DESCRIPTION,
    version=config.API_VERSION,
    debug=config.DEBUG,
    openapi_version="3.0.2",  # 设置OpenAPI版本
    # 添加路由分组的标签描述
    openapi_tags=[
        {
            "name": "system",
            "description": "系统接口",
        },
        {
            "name": "analyze",
            "description": "解析url",
        },
        {
            "name": "idphoto",
            "description": "证件照处理接口",
        },
        {
            "name": "inpainting",
            "description": "图像修复接口",
        },
        {
            "name": "youtube",
            "description": "YouTube视频下载接口",
        }
    ]
)

# 应用启动和关闭事件
@app.on_event("startup")
async def startup_event():
    """应用启动时的事件处理"""
    logger.info(f"API 服务启动 - 环境: {current_env}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的事件处理"""
    logger.info("API 服务关闭")

# Root endpoint
@app.get("/")
async def root():
    """根端点，返回 API 信息"""
    logger.info("访问根端点")
    return {
        "message": f"欢迎使用数据分析 API - {current_env} 环境",
        "status": "运行中",
        "文档": "/docs",
        "环境": current_env
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """健康检查端点"""
    logger.info("执行健康检查123131")
    return {"status": "健康", "环境": current_env}
    
# 注册所有路由模块
from src.routes import register_routes
register_routes(app)

# 注册所有 controller 模块
from src.controllers.index import register_controllers
register_controllers(app)

# 配置 uvicorn 使用文件日志而不是控制台输出
def configure_uvicorn_logging():
    """配置 uvicorn 使用文件日志"""
    # 关闭 uvicorn 默认日志
    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []
    
    # 让 uvicorn 使用我们的日志器
    logging.getLogger("uvicorn").parent = logging.getLogger("app")
    logging.getLogger("uvicorn.access").parent = logging.getLogger("app")

# Run the application with uvicorn when this script is executed directly
if __name__ == "__main__":
    # 配置 uvicorn 日志
    configure_uvicorn_logging()
    
    # 开始服务
    logger.info(f"启动 uvicorn 服务 - 主机: {config.HOST}, 端口: {config.PORT}")
    
    # 使用配置中的参数
    uvicorn.run(
        "main:app",                  # Import string to your app
        host=config.HOST,            # Host to bind the server to
        port=config.PORT,            # Port to bind the server to
        reload=config.RELOAD,        # Auto-reload when code changes
        log_level=config.LOG_LEVEL.lower(),  # Log level
        workers=1,                   # Number of worker processes
        log_config=None,             # 禁用 uvicorn 默认日志配置
        access_log=False,            # 禁用 uvicorn 访问日志
        openapi_version="3.0.2"
    )
