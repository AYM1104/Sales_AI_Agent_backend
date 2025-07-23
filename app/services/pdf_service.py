import io
from datetime import datetime
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

class PDFService:
    """PDF生成サービス"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_japanese_font()
        self._setup_custom_styles()
    
    def _setup_japanese_font(self):
        """日本語フォントの設定"""
        try:
            # システムにある日本語フォントを試行
            font_paths = [
                # Windows
                "C:/Windows/Fonts/NotoSansCJK-Regular.ttc",
                "C:/Windows/Fonts/msgothic.ttc",
                # macOS
                "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
                "/Library/Fonts/Arial Unicode MS.ttf",
                # Linux
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Japanese', font_path))
                    break
            else:
                # フォントが見つからない場合はデフォルトを使用
                print("Warning: Japanese font not found, using default font")
        except Exception as e:
            print(f"Font setup error: {e}")
    
    def _setup_custom_styles(self):
        """カスタムスタイルの設定"""
        self.styles.add(ParagraphStyle(
            name='JapaneseTitle',
            parent=self.styles['Title'],
            fontName='Japanese',
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='JapaneseHeading',
            parent=self.styles['Heading1'],
            fontName='Japanese',
            fontSize=14,
            spaceAfter=12,
            spaceBefore=12,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='JapaneseNormal',
            parent=self.styles['Normal'],
            fontName='Japanese',
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT
        ))
        
        self.styles.add(ParagraphStyle(
            name='JapaneseSmall',
            parent=self.styles['Normal'],
            fontName='Japanese',
            fontSize=8,
            spaceAfter=4,
            alignment=TA_LEFT
        ))
    
    def generate_analysis_report(
        self, 
        company_data: Dict[str, str], 
        results: Dict[str, str],
        solutions: list
    ) -> io.BytesIO:
        """分析レポートPDFを生成"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # タイトル
        title = Paragraph("顧客理解AIエージェント 分析結果レポート", self.styles['JapaneseTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # 生成日時
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        date_info = Paragraph(f"生成日時: {current_time}", self.styles['JapaneseSmall'])
        story.append(date_info)
        story.append(Spacer(1, 20))
        
        # 企業情報セクション
        story.append(Paragraph("企業情報", self.styles['JapaneseHeading']))
        
        company_info_data = [
            ["項目", "内容"],
            ["企業名", company_data.get('company_name', 'N/A')],
            ["部署名", company_data.get('department_name', 'N/A')],
            ["役職", company_data.get('position_name', 'N/A')],
            ["業務範囲", company_data.get('job_scope', 'N/A')]
        ]
        
        company_table = Table(company_info_data, colWidths=[2*inch, 4*inch])
        company_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Japanese'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(company_table)
        story.append(Spacer(1, 20))
        
        # 各セクションを追加
        sections = [
            ("有価証券報告書要約", results.get('summary', '')),
            ("仮説・担当者課題", results.get('hypothesis', '')),
            ("ソリューションマッチング", results.get('matching_result', '')),
            ("ヒアリング項目", results.get('hearing_items', ''))
        ]
        
        for section_title, content in sections:
            if content:
                story.append(Paragraph(section_title, self.styles['JapaneseHeading']))
                
                # 長いテキストを段落に分割
                paragraphs = content.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        story.append(Paragraph(para.strip(), self.styles['JapaneseNormal']))
                
                story.append(Spacer(1, 15))
        
        # ソリューション一覧
        if solutions:
            story.append(Paragraph("弊社IoTソリューション一覧", self.styles['JapaneseHeading']))
            
            solution_data = [["ソリューション名", "特徴", "主な用途"]]
            for solution in solutions:
                solution_data.append([
                    solution.get('name', ''),
                    solution.get('features', ''),
                    solution.get('use_case', '')
                ])
            
            solution_table = Table(solution_data, colWidths=[2*inch, 2.5*inch, 2.5*inch])
            solution_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Japanese'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(solution_table)
        
        # フッター
        story.append(Spacer(1, 30))
        footer = Paragraph(
            "このレポートは顧客理解AIエージェントによって自動生成されました。",
            self.styles['JapaneseSmall']
        )
        story.append(footer)
        
        # PDFを生成
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def generate_simple_text_pdf(self, text: str, title: str = "レポート") -> io.BytesIO:
        """シンプルなテキストPDFを生成"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        story = []
        story.append(Paragraph(title, self.styles['JapaneseTitle']))
        story.append(Spacer(1, 20))
        
        # テキストを段落に分割
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), self.styles['JapaneseNormal']))
                story.append(Spacer(1, 10))
        
        doc.build(story)
        buffer.seek(0)
        
        return buffer