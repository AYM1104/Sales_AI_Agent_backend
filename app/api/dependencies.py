from fastapi import Depends, HTTPException, status
from typing import Annotated
import logging
from app.config import settings
from app.services.company_service import CompanyService
from app.services.solution_service import SolutionService
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

# API Key validation
async def verify_api_key():
    """Google API キーの検証"""
    if not settings.GOOGLE_API_KEY:
        logger.error("Google API キーが設定されていません")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google API キーが設定されていません"
        )
    return True

# Service dependencies
async def get_company_service() -> CompanyService:
    """CompanyServiceの依存性注入"""
    return CompanyService()

async def get_solution_service() -> SolutionService:
    """SolutionServiceの依存性注入"""
    return SolutionService()

async def get_gemini_service() -> GeminiService:
    """GeminiServiceの依存性注入"""
    return GeminiService()

# Rate limiting (将来的な拡張用)
class RateLimiter:
    """レート制限クラス（将来的な実装用）"""
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
    
    async def __call__(self):
        # 実際のレート制限ロジックはここに実装
        # 現在はパススルー
        return True

# Request validation
async def validate_company_name(company_name: str):
    """企業名のバリデーション"""
    if not company_name or len(company_name.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="企業名は必須です"
        )
    
    if len(company_name) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="企業名は100文字以内で入力してください"
        )
    
    return company_name.strip()

# Common dependencies
ApiKeyDep = Annotated[bool, Depends(verify_api_key)]
CompanyServiceDep = Annotated[CompanyService, Depends(get_company_service)]
SolutionServiceDep = Annotated[SolutionService, Depends(get_solution_service)]
GeminiServiceDep = Annotated[GeminiService, Depends(get_gemini_service)]
RateLimitDep = Annotated[bool, Depends(RateLimiter())]