from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router
from app.api.pdf_routes import router as pdf_router

def create_app() -> FastAPI:
    """FastAPIアプリケーションを作成"""
    app = FastAPI(
        title="顧客理解AIエージェント API",
        description="企業分析とソリューション提案API",
        version="1.0.0"
    )

    # CORS設定
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ルーターを登録
    app.include_router(router)
    app.include_router(pdf_router)

    return app

app = create_app()