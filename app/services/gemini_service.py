import os
import fitz  # PyMuPDF
import requests
from typing import List
from google.generativeai import GenerativeModel
import google.generativeai as genai
from app.config import settings
from app.models.schemas import Solution

class GeminiService:
    """Gemini API サービス"""
    
    def __init__(self):
        print(f"=== GeminiService初期化開始 ===")
        print(f"GOOGLE_API_KEY存在: {bool(settings.GOOGLE_API_KEY)}")
        print(f"GEMINI_MODEL_NAME: {settings.GEMINI_MODEL_NAME}")
        
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY が設定されていません")
        
        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            print("genai.configure 成功")
            
            self.model = GenerativeModel(model_name=settings.GEMINI_MODEL_NAME)
            print("GenerativeModel 作成成功")
            
        except Exception as e:
            print(f"GeminiService初期化エラー: {e}")
            print(f"エラータイプ: {type(e)}")
            raise
        
        print("=== GeminiService初期化完了 ===")
    
    def _load_prompt(self, filename: str) -> str:
        """プロンプトファイルを読み込み"""
        filepath = os.path.join(settings.PROMPTS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    async def summarize_securities_report(self, pdf_url: str, company_name: str) -> str:
        """有価証券報告書を要約"""
        # 複雑な処理を全部スキップして、シンプルなAPIコールのみ
        try:
            print("=== シンプルテスト開始 ===")
            simple_prompt = "Hello, how are you?"
            print(f"シンプルプロンプト: {simple_prompt}")
            
            response = self.model.generate_content(simple_prompt)
            print("シンプルテスト成功！")
            
            return f"テスト成功: {response.text}"
        except Exception as e:
            print(f"シンプルテストでもエラー: {e}")
            return f"シンプルテストでもエラー: {e}"
    
    # async def summarize_securities_report(self, pdf_url: str, company_name: str) -> str:
    #     """有価証券報告書を要約"""
    #     try:
    #         print(f"=== summarize_securities_report 開始 ===")
    #         print(f"PDF URL: {pdf_url}")
    #         print(f"企業名: {company_name}")
            
    #         # 1. PDFデータをダウンロード
    #         print("PDFダウンロード開始...")
    #         response = requests.get(pdf_url)
    #         response.raise_for_status()
    #         print(f"PDFダウンロード成功: {len(response.content)} bytes")
            
    #         # 2. fitz で PDF を読み込む
    #         print("PDF読み込み開始...")
    #         doc = fitz.open(stream=response.content, filetype="pdf")
    #         print(f"PDF読み込み成功: {len(doc)} pages")
            
    #         # 3. テキスト抽出
    #         print("テキスト抽出開始...")
    #         text = ""
    #         for page in doc:
    #             text += page.get_text()
    #         print(f"テキスト抽出成功: {len(text)} 文字")
            
    #         # 4. プロンプトファイルを読み込む
    #         print("プロンプト読み込み開始...")
    #         prompt_template = self._load_prompt("prompt.txt")
    #         print(f"プロンプトテンプレート読み込み成功: {len(prompt_template)} 文字")
            
    #         prompt_text = prompt_template.replace("[企業名を入力]", company_name) + "\n" + text[:settings.MAX_PDF_CHARS]
    #         print(f"最終プロンプト準備完了: {len(prompt_text)} 文字")
    #         print(f"MAX_PDF_CHARS設定: {settings.MAX_PDF_CHARS}")
            
    #         # 5. Gemini APIで要約を取得
    #         print("Gemini API呼び出し開始...")
    #         print(f"使用モデル: {settings.GEMINI_MODEL_NAME}")
            
    #         response = self.model.generate_content(prompt_text)
    #         print("Gemini API呼び出し成功")
    #         print(f"レスポンス取得: {len(response.text) if response.text else 0} 文字")
            
    #         return response.text
            
    #     except requests.RequestException as e:
    #         print(f"PDFダウンロードエラー: {e}")
    #         raise
    #     except Exception as e:
    #         print(f"summarize_securities_report エラー: {e}")
    #         print(f"エラータイプ: {type(e)}")
    #         import traceback
    #         print(f"スタックトレース: {traceback.format_exc()}")
    #         raise
    
    async def generate_hypothesis(
        self, 
        summary: str, 
        department_name: str, 
        position_name: str, 
        job_scope: str
    ) -> str:
        """仮説を生成"""
        prompt_template = self._load_prompt("hypothesis_prompt.txt")
        prompt = prompt_template.replace("{securities_report_summary}", summary)
        prompt = prompt.replace("{department_name}", department_name)
        prompt = prompt.replace("{position_title}", position_name)
        prompt = prompt.replace("{job_scope}", job_scope)
        
        response = self.model.generate_content(prompt)
        return response.text
    
    async def match_solutions(self, hypothesis: str, solutions: List[Solution]) -> str:
        """ソリューションマッチング"""
        prompt_template = self._load_prompt("solution_matching_prompt.txt")
        
        solutions_text = "\n".join([
            f"・{s.name}：{s.features}（用途：{s.use_case}）"
            for s in solutions
        ])
        
        prompt = prompt_template.replace("{hypothesis}", hypothesis)
        prompt = prompt.replace("{solutions}", solutions_text)
        
        response = self.model.generate_content(prompt)
        return response.text
    
    async def generate_hearing_items(
        self,
        company_name: str,
        department_name: str,
        position_name: str,
        hypothesis: str
    ) -> str:
        """ヒアリング項目を生成"""
        prompt_template = self._load_prompt("hearing_prompt.txt")
        
        prompt = prompt_template.replace("{company_name}", company_name)
        prompt = prompt.replace("{department_name}", department_name)
        prompt = prompt.replace("{position_name}", position_name)
        prompt = prompt.replace("{company_size}", "")
        prompt = prompt.replace("{industry}", "")
        prompt = prompt.replace("{hypothesis}", hypothesis)
        
        response = self.model.generate_content(prompt)
        return response.text
