from pydantic import BaseModel, Field
from typing import List, Optional

# リクエストモデル
class CompanySearchRequest(BaseModel):
    """企業検索リクエスト"""
    company_name: str = Field(..., description="企業名", min_length=1)
    department_name: Optional[str] = Field("", description="部署名")
    position_name: Optional[str] = Field("", description="役職名")
    job_scope: Optional[str] = Field("", description="業務範囲")

class SolutionMatchRequest(BaseModel):
    """ソリューションマッチングリクエスト"""
    hypothesis: str = Field(..., description="仮説", min_length=1)

# レスポンスモデル
class Solution(BaseModel):
    """ソリューション情報"""
    name: str = Field(..., description="ソリューション名")
    features: str = Field(..., description="特徴")
    use_case: str = Field(..., description="用途")

class CompanySearchResponse(BaseModel):
    """企業検索レスポンス"""
    success: bool = Field(..., description="成功フラグ")
    summary: Optional[str] = Field("", description="要約")
    hypothesis: Optional[str] = Field("", description="仮説")
    hearing_items: Optional[str] = Field("", description="ヒアリング項目")
    matching_result: Optional[str] = Field("", description="マッチング結果")
    error_message: Optional[str] = Field("", description="エラーメッセージ")

class SolutionsResponse(BaseModel):
    """ソリューション一覧レスポンス"""
    success: bool = Field(..., description="成功フラグ")
    solutions: List[Solution] = Field([], description="ソリューション一覧")

class HealthResponse(BaseModel):
    """ヘルスチェックレスポンス"""
    message: str = Field(..., description="メッセージ")
    status: str = Field("ok", description="ステータス")