from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    CompanySearchRequest,
    CompanySearchResponse,
    SolutionsResponse,
    HealthResponse
)
from app.api.dependencies import (
    ApiKeyDep,
    CompanyServiceDep,
    SolutionServiceDep,
    RateLimitDep
)

router = APIRouter()

@router.get("/", response_model=HealthResponse)
async def health_check():
    """ヘルスチェック"""
    return HealthResponse(message="顧客理解AIエージェント API")

@router.get("/solutions", response_model=SolutionsResponse)
async def get_solutions(
    solution_service: SolutionServiceDep,
    _: RateLimitDep
):
    """ソリューション一覧を取得"""
    try:
        solutions = solution_service.get_solutions()
        return SolutionsResponse(success=True, solutions=solutions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search-company", response_model=CompanySearchResponse)
async def search_company(
    request: CompanySearchRequest,
    company_service: CompanyServiceDep,
    _api_key: ApiKeyDep,
    _rate_limit: RateLimitDep
):
    """企業検索・分析を実行"""
    try:
        result = await company_service.analyze_company(request)
        return result
    except Exception as e:
        return CompanySearchResponse(
            success=False,
            error_message=f"APIサーバーエラー: {str(e)}"
        )


@router.get("/debug/env-direct")
async def env_direct():
    import os
    return {
        "google_api_key_raw": os.environ.get('GOOGLE_API_KEY', 'NOT_FOUND'),
        "google_api_key_getenv": os.getenv('GOOGLE_API_KEY', 'NOT_FOUND'),
        "google_api_key_exists": 'GOOGLE_API_KEY' in os.environ,
        "all_env_keys": list(os.environ.keys()),
        "port": os.getenv('PORT'),
        "total_vars": len(os.environ)
    }
