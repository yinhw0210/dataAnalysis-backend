from fastapi import FastAPI
from .analyze import router as analyze_router
from .system import router as system_router
from .idphoto import router as idphoto_router
from .doubao import router as doubao_router

def register_routes(app: FastAPI):
    # 豆包去水印路由 - 优先级最高，放在最前面
    app.include_router(doubao_router)
    app.include_router(analyze_router)
    app.include_router(system_router)
    app.include_router(idphoto_router)