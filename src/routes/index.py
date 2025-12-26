from fastapi import FastAPI
from .analyze import router as analyze_router
from .system import router as system_router
from .idphoto import router as idphoto_router

def register_routes(app: FastAPI):
    app.include_router(analyze_router)
    app.include_router(system_router)
    app.include_router(idphoto_router)