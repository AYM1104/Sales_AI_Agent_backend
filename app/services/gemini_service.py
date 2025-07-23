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
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = GenerativeModel(model_name=settings.GEMINI_MODEL_NAME)
    
    def _load_prompt(self, filename: str) -> str:
        """プロンプトファイルを読み込み"""
        filepath = os.path.join(settings.PROMPTS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    
    async def summarize_securities_report(self, pdf_url: str, company_name: str) -> str:
        """有価証券報告書を要約"""
        # 1. PDFデータをダウンロード
        response = requests.get(pdf_url)
        response.raise_for_status()
        
        # 2. fitz で PDF を読み込む
        doc = fitz.open(stream=response.content, filetype="pdf")
        
        # 3. テキスト抽出
        text = ""
        for page in doc:
            text += page.get_text()
        
        # 4. プロンプトファイルを読み込む
        prompt_template = self._load_prompt("prompt.txt")
        prompt_text = prompt_template.replace("[企業名を入力]", company_name) + "\n" + text[:settings.MAX_PDF_CHARS]
        
        # 5. Gemini APIで要約を取得
        response = self.model.generate_content(prompt_text)
        return response.text
    
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