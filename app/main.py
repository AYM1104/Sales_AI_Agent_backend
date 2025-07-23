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

    # ★ここに追加 - 起動時イベント
    @app.on_event("startup")
    async def startup_event():
        print("=== 環境変数確認 ===")
        
        # 全ての環境変数を確認
        import os
        all_vars = dict(os.environ)
        print(f"全環境変数数: {len(all_vars)}")
        
        # Google関連の変数を探す
        google_vars = {k: v for k, v in all_vars.items() if 'GOOGLE' in k.upper()}
        print(f"Google関連変数: {google_vars}")
        
        # 具体的に確認
        api_key = os.getenv('GOOGLE_API_KEY')
        print(f"GOOGLE_API_KEY: {api_key is not None}")
        if api_key:
            print(f"キーの長さ: {len(api_key)}")
            print(f"最初の10文字: {api_key[:10]}...")
        
        print("================")

    # ルーターを登録
    app.include_router(router)
    app.include_router(pdf_router)

    return app

app = create_app()
