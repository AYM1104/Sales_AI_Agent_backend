import logging
from app.models.schemas import CompanySearchRequest, CompanySearchResponse
from app.services.gemini_service import GeminiService
from app.services.solution_service import SolutionService
from app.utils.web_scraper import WebScraper
from app.data.company_codes import company_codes

logger = logging.getLogger(__name__)

class CompanyService:
    """企業分析サービス"""
    
    def __init__(self):
        self.gemini_service = GeminiService()
        self.solution_service = SolutionService()
        self.web_scraper = WebScraper()
    
    def get_company_code(self, company_name: str) -> str:
        """企業名から企業コードを取得"""
        return company_codes.get(company_name)
    
    async def analyze_company(self, request: CompanySearchRequest) -> CompanySearchResponse:
        """企業分析を実行"""
        try:
            logger.info(f"企業分析開始: {request.company_name}")
            
            # 企業コードを取得
            code = self.get_company_code(request.company_name)
            logger.info(f"企業コード: {code}")
            
            if not code:
                return CompanySearchResponse(
                    success=False,
                    error_message="指定された企業名が辞書に存在しません。先に企業コードを登録してください。"
                )
            
            # 有価証券報告書PDFを取得
            pdf_url = self.web_scraper.fetch_securities_report_pdf(code)
            logger.info(f"PDF URL: {pdf_url}")
            
            if not pdf_url:
                return CompanySearchResponse(
                    success=False,
                    error_message="PDFリンクが見つかりませんでした。"
                )
            
            # 要約を生成
            summary = await self.gemini_service.summarize_securities_report(
                pdf_url, request.company_name
            )
            logger.info("要約取得成功")
            
            hypothesis = ""
            hearing_items = ""
            matching_result = ""
            
            # 部署名と役職が入力されている場合、仮説とヒアリング項目を生成
            if request.department_name and request.position_name:
                # 仮説生成
                hypothesis = await self.gemini_service.generate_hypothesis(
                    summary, request.department_name, 
                    request.position_name, request.job_scope
                )
                logger.info("仮説取得成功")
                
                # ソリューションマッチング
                if hypothesis:
                    solutions = self.solution_service.get_solutions()
                    matching_result = await self.gemini_service.match_solutions(
                        hypothesis, solutions
                    )
                    logger.info("マッチング取得成功")
                
                # ヒアリング項目生成
                hearing_items = await self.gemini_service.generate_hearing_items(
                    request.company_name, request.department_name,
                    request.position_name, hypothesis
                )
                logger.info("ヒアリング項目取得成功")
            
            return CompanySearchResponse(
                success=True,
                summary=summary,
                hypothesis=hypothesis,
                hearing_items=hearing_items,
                matching_result=matching_result
            )
            
        except Exception as e:
            logger.error(f"企業分析エラー: {str(e)}")
            raise e