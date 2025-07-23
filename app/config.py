import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """アプリケーション設定"""
    
    # API設定
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "顧客理解AIエージェント"
    
    # CORS設定
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://sales-ai-agent-frontend-git-main-ak3668134-gmailcoms-projects.vercel.app",
        "https://sales-ai-agent-frontend.vercel.app",
    ]
    
    # Google AI設定
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL_NAME: str = "gemini-2.5-pro"
    
    # ファイルパス設定
    DATA_DIR: str = "app/data"
    PROMPTS_DIR: str = "app/data/prompts"
    SOLUTIONS_FILE: str = "app/data/solutions.json"
    
    # PDF処理設定
    MAX_PDF_CHARS: int = 90000

settings = Settings()
