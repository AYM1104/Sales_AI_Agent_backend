import json
from typing import List
from app.config import settings
from app.models.schemas import Solution

class SolutionService:
    """ソリューション管理サービス"""
    
    def get_solutions(self) -> List[Solution]:
        """ソリューション一覧を取得"""
        with open(settings.SOLUTIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return [Solution(**item) for item in data]