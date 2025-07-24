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
        try:
            print("=== プロンプトファイル版テスト開始 ===")
            print(f"企業名: {company_name}")
            
            # 1. プロンプトテンプレートを読み込み
            print("プロンプトテンプレート読み込み...")
            prompt_template = self._load_prompt("prompt.txt")
            print(f"プロンプトテンプレート: {len(prompt_template)} 文字")
            
            # 2. 企業名を置換
            prompt_text = prompt_template.replace("[企業名を入力]", company_name)
            print(f"企業名置換後: {len(prompt_text)} 文字")
            
            # 3. ダミーの企業情報を追加（PDF代わり）
            dummy_company_info = f"""
    
    {company_name}の有価証券報告書（サンプル情報）:
    
    ■事業概況
    - 主力事業：IT・ソフトウェア開発
    - 売上高：前年度100億円（前年比5%増）
    - 営業利益：10億円（利益率10%）
    - 従業員数：1,000名
    
    ■事業リスク
    - 人材不足による開発遅延リスク
    - 技術革新への対応遅れ
    - サイバーセキュリティリスク
    
    ■設備投資
    - 前年度設備投資額：5億円
    - IT・システム投資：2億円
    - 今後3年間でDX推進に10億円投資予定
    
    ■組織体制
    - 事業部制を採用
    - 製造部門、開発部門、営業部門
    - 子会社3社（うち海外1社）
    
    ■競合環境
    - 業界内でのシェア：10%（業界5位）
    - 差別化課題：品質向上、コスト削減
    - 顧客要求：納期短縮、自動化推進
            """
            
            # 4. 最終的なプロンプトを作成
            final_prompt = prompt_text + dummy_company_info
            print(f"最終プロンプト: {len(final_prompt)} 文字")
            
            # 5. Gemini APIで分析を実行
            print("Gemini API呼び出し開始...")
            response = self.model.generate_content(final_prompt)
            print("Gemini API呼び出し成功!")
            print(f"レスポンス長: {len(response.text)} 文字")
            
            return response.text
            
        except Exception as e:
            print(f"プロンプトファイル版テストエラー: {e}")
            import traceback
            print(f"スタックトレース: {traceback.format_exc()}")
            return f"エラー: {e}"    

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
