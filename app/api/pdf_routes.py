from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import io
from datetime import datetime
from app.services.pdf_service import PDFService
from app.models.schemas import Solution

router = APIRouter(prefix="/pdf", tags=["PDF"])

class PDFGenerateRequest(BaseModel):
    """PDF生成リクエスト"""
    company_data: Dict[str, str]
    results: Dict[str, str]
    solutions: List[Dict[str, str]] = []

class SimplePDFRequest(BaseModel):
    """シンプルPDF生成リクエスト"""
    text: str
    title: str = "レポート"

@router.post("/generate-report")
async def generate_analysis_report(request: PDFGenerateRequest):
    """分析レポートPDFを生成"""
    try:
        pdf_service = PDFService()
        pdf_buffer = pdf_service.generate_analysis_report(
            company_data=request.company_data,
            results=request.results,
            solutions=request.solutions
        )
        
        # ファイル名を生成
        company_name = request.company_data.get('company_name', '企業')
        current_date = datetime.now().strftime("%Y%m%d")
        filename = f"{company_name}_分析結果_{current_date}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF生成エラー: {str(e)}")

@router.post("/generate-simple")
async def generate_simple_pdf(request: SimplePDFRequest):
    """シンプルなテキストPDFを生成"""
    try:
        pdf_service = PDFService()
        pdf_buffer = pdf_service.generate_simple_text_pdf(
            text=request.text,
            title=request.title
        )
        
        # ファイル名を生成
        current_date = datetime.now().strftime("%Y%m%d")
        filename = f"{request.title}_{current_date}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF生成エラー: {str(e)}")

@router.get("/test")
async def test_pdf_generation():
    """PDF生成テスト"""
    try:
        pdf_service = PDFService()
        test_text = "これはPDF生成のテストです。\n\n日本語フォントが正しく表示されているかを確認します。"
        pdf_buffer = pdf_service.generate_simple_text_pdf(test_text, "テストレポート")
        
        return StreamingResponse(
            io.BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=test_report.pdf"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"テストPDF生成エラー: {str(e)}")