import requests
from bs4 import BeautifulSoup
import re
from typing import Optional

class WebScraper:
    """Webスクレイピングユーティリティ"""
    
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0"}
    
    def fetch_securities_report_pdf(self, code: str) -> Optional[str]:
        """企業コードから有価証券報告書PDFのURLを取得"""
        url = f"https://www.nikkei.com/nkd/company/ednr/?scode={code}"
        
        try:
            res = requests.get(url, headers=self.headers)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            
            # 「有価証券報告書」を含むリンクを抽出
            links = soup.find_all("a", string=re.compile("有価証券報告書"))
            
            for link in links:
                href = link.get("href")
                if not href:
                    continue
                
                full_url = requests.compat.urljoin(url, href)
                
                # PDFのURLを抽出
                pdf_url = self._extract_pdf_url(full_url)
                if pdf_url:
                    return pdf_url
            
            return None
            
        except Exception as e:
            print(f"PDF取得エラー: {e}")
            return None
    
    def _extract_pdf_url(self, page_url: str) -> Optional[str]:
        """ページからPDFのURLを抽出"""
        try:
            res = requests.get(page_url, headers=self.headers)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            
            # JavaScriptからPDFパスを抽出
            script_text = "".join([
                script.get_text() for script in soup.find_all("script")
            ])
            
            match = re.search(r"window\['pdfLocation'\]\s*=\s*\"(.*?)\"", script_text)
            if match:
                pdf_path = match.group(1)
                return f"https://www.nikkei.com{pdf_path}"
            
            return None
            
        except Exception as e:
            print(f"PDF URL抽出エラー: {e}")
            return None