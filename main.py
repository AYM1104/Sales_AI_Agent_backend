from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import backend.app.data.company_codes as company_codes
import json
import requests
from bs4 import BeautifulSoup
import re
import fitz  # PyMuPDF
import os
from dotenv import load_dotenv
from google.generativeai import GenerativeModel
import google.generativeai as genai

# 環境変数の読み込み
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Gemini APIキーを設定
genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Next.jsのデフォルトポート
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# リクエストモデル
class CompanySearchRequest(BaseModel):
    company_name: str
    department_name: str = ""
    position_name: str = ""
    job_scope: str = ""

class SolutionMatchRequest(BaseModel):
    hypothesis: str

# レスポンスモデル
class CompanySearchResponse(BaseModel):
    success: bool
    summary: str = ""
    hypothesis: str = ""
    hearing_items: str = ""
    matching_result: str = ""
    error_message: str = ""

# 企業名から企業コードを取得する関数
def get_company_code(company_name):
    code = company_codes.company_codes.get(company_name)
    return code

# 企業コードから有価証券報告書PDFを取得する関数
def fetch_securities_report_pdf(code):
    url = "https://www.nikkei.com/nkd/company/ednr/?scode=" + code
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    # 「有価証券報告書」を含むリンクを抽出
    links = soup.find_all("a", string=re.compile("有価証券報告書"))
    pdf_url = None
    for link in links:
        href = link.get("href")
        full_url = requests.compat.urljoin(url, href)

        # ページを取得
        res2 = requests.get(full_url, headers=headers)
        soup2 = BeautifulSoup(res2.text, "html.parser")
        script_text = "".join([script.get_text() for script in soup2.find_all("script")])
        match = re.search(r"window\['pdfLocation'\]\s*=\s*\"(.*?)\"", script_text)
        if match:
            pdf_path = match.group(1)
            pdf_url = "https://www.nikkei.com" + pdf_path
            break

    return pdf_url

# PDFからテキスト抽出・要約プロンプト生成・Gemini API呼び出し関数
def summarize_securities_report(pdf_url, company_name):
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
    with open("prompt.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    max_chars = 90000
    prompt_text = prompt_template.replace("[企業名を入力]", company_name) + "\n" + text[:max_chars]

    # 5. Gemini APIで要約を取得
    model = GenerativeModel(model_name="gemini-2.5-pro")
    response = model.generate_content(prompt_text)

    return response.text

# ソリューション一覧の読み込み
def load_solutions(filepath="solutions.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# ソリューションマッチングAI出力
def match_solutions(hypothesis, solutions):
    with open("solution_matching_prompt.txt", "r", encoding="utf-8") as f:
        match_prompt_template = f.read()
    solutions_text = "\n".join([
        f"・{s['name']}：{s['features']}（用途：{s['use_case']}）"
        for s in solutions
    ])
    match_prompt = match_prompt_template.replace("{hypothesis}", hypothesis)
    match_prompt = match_prompt.replace("{solutions}", solutions_text)
    model = GenerativeModel(model_name="gemini-2.5-pro")
    response = model.generate_content(match_prompt)
    return response.text

# API エンドポイント
@app.get("/")
async def root():
    return {"message": "顧客理解AIエージェント API"}

@app.get("/solutions")
async def get_solutions():
    try:
        solutions = load_solutions()
        return {"success": True, "solutions": solutions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-company")
async def search_company(request: CompanySearchRequest):
    try:
        print("リクエスト:", request.dict())
        # 企業コードを取得
        code = get_company_code(request.company_name)
        print("企業コード:", code)
        if not code:
            return CompanySearchResponse(
                success=False,
                error_message="指定された企業名が辞書に存在しません。先に企業コードを登録してください。"
            )

        # 有価証券報告書PDFを取得
        pdf_url = fetch_securities_report_pdf(code)
        print("PDF URL:", pdf_url)
        if not pdf_url:
            return CompanySearchResponse(
                success=False,
                error_message="PDFリンクが見つかりませんでした。"
            )

        # 要約を生成
        summary = summarize_securities_report(pdf_url, request.company_name)
        print("要約取得成功")

        hypothesis = ""
        hearing_items = ""
        matching_result = ""

        # 部署名と役職が入力されている場合、仮説とヒアリング項目を生成
        if request.department_name and request.position_name:
            # 仮説生成
            with open("hypothesis_prompt.txt", "r", encoding="utf-8") as f:
                hypo_template = f.read()
            hypo_prompt = hypo_template.replace("{securities_report_summary}", summary)
            hypo_prompt = hypo_prompt.replace("{department_name}", request.department_name)
            hypo_prompt = hypo_prompt.replace("{position_title}", request.position_name)
            hypo_prompt = hypo_prompt.replace("{job_scope}", request.job_scope)
            model = GenerativeModel(model_name="gemini-2.5-pro")
            response = model.generate_content(hypo_prompt)
            hypothesis = response.text
            print("仮説取得成功")

            # ソリューションマッチング
            if hypothesis:
                solutions = load_solutions()
                matching_result = match_solutions(hypothesis, solutions)
                print("マッチング取得成功")

            # ヒアリング項目生成
            with open("hearing_prompt.txt", "r", encoding="utf-8") as f:
                hearing_template = f.read()
            hearing_prompt = hearing_template.replace("{company_name}", request.company_name)
            hearing_prompt = hearing_prompt.replace("{department_name}", request.department_name)
            hearing_prompt = hearing_prompt.replace("{position_name}", request.position_name)
            hearing_prompt = hearing_prompt.replace("{company_size}", "")
            hearing_prompt = hearing_prompt.replace("{industry}", "")
            hearing_prompt = hearing_prompt.replace("{hypothesis}", hypothesis)
            hearing_response = model.generate_content(hearing_prompt)
            hearing_items = hearing_response.text
            print("ヒアリング項目取得成功")

        return CompanySearchResponse(
            success=True,
            summary=summary,
            hypothesis=hypothesis,
            hearing_items=hearing_items,
            matching_result=matching_result
        )

    except Exception as e:
        print("APIエラー:", str(e))
        return CompanySearchResponse(
            success=False,
            error_message=f"APIサーバーエラー: {str(e)}"
        )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
