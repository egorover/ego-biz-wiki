import os
import glob
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

windows_font_path = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'arial.ttf')
if os.path.exists(windows_font_path):
    pdfmetrics.registerFont(TTFont('ArialCustom', windows_font_path))
    FONT_NAME = 'ArialCustom'
else:
    FONT_NAME = 'Helvetica'

def build_pdf():
    pdf_path = os.path.join("submission", "knowledge_base.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', fontName=FONT_NAME, fontSize=28, leading=34, alignment=1, spaceAfter=15)
    subtitle_style = ParagraphStyle('SubTitleStyle', fontName=FONT_NAME, fontSize=14, leading=18, alignment=1, spaceAfter=30, textColor=colors.gray)
    h1_style = ParagraphStyle('H1Style', fontName=FONT_NAME, fontSize=20, leading=24, spaceBefore=15, spaceAfter=10, textColor=colors.HexColor("#1A365D"))
    h2_style = ParagraphStyle('H2Style', fontName=FONT_NAME, fontSize=14, leading=18, spaceBefore=10, spaceAfter=6, textColor=colors.HexColor("#2B6CB0"))
    body_style = ParagraphStyle('BodyStyle', fontName=FONT_NAME, fontSize=10, leading=14, spaceAfter=8)
    meta_style = ParagraphStyle('MetaStyle', fontName=FONT_NAME, fontSize=10, leading=14, textColor=colors.HexColor("#4A5568"))

    story = []
    story.append(Spacer(1, 150))
    story.append(Paragraph("<b>EgoBiz Wiki</b>", title_style))
    story.append(Paragraph("Corporate Knowledge Base", subtitle_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Demo Company:</b> EgoTech Solutions", body_style))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d.%m.%Y')}", body_style))
    story.append(Paragraph("<b>Version:</b> 1.0 (Artifact Submission)", body_style))
    story.append(PageBreak())

    story.append(Paragraph("Table of Contents", h1_style))
    story.append(Spacer(1, 10))
    
    kb_path = "knowledge_base"
    md_files = sorted(glob.glob(os.path.join(kb_path, "**", "*.md"), recursive=True))
    
    categories = {}
    for file_path in md_files:
        rel_path = os.path.relpath(file_path, kb_path)
        category = os.path.dirname(rel_path)
        title = os.path.basename(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('# '):
                    title = line.replace('# ', '').strip()
                    break
        if category not in categories:
            categories[category] = []
        categories[category].append(title)

    for cat, titles in categories.items():
        story.append(Paragraph(f"<b>Раздел: {cat}</b>", h2_style))
        for t in titles:
            story.append(Paragraph(f"• {t}", body_style))
    story.append(PageBreak())

    for file_path in md_files:
        rel_path = os.path.relpath(file_path, kb_path)
        category = os.path.dirname(rel_path)
        story.append(Paragraph(f"Категория: {category}", meta_style))
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                if line.startswith('# '):
                    story.append(Paragraph(line.replace('# ', ''), h1_style))
                elif line.startswith('## '):
                    story.append(Paragraph(line.replace('## ', ''), h2_style))
                else:
                    clean_line = line.replace('**', '<b>', 1).replace('**', '</b>', 1)
                    story.append(Paragraph(clean_line, body_style))
                    
        story.append(Spacer(1, 15))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey, spaceAfter=20))
    
    story.append(PageBreak())
    story.append(Paragraph("Technical Summary", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>Documents Processed:</b> {len(md_files)}", body_style))
    story.append(Paragraph("<b>Format:</b> Markdown source converted to PDF", body_style))
    story.append(Paragraph(f"<b>Categories Count:</b> {len(categories)}", body_style))
    story.append(Paragraph("<b>Purpose:</b> Source knowledge base for the EgoBiz Wiki RAG MVP.", body_style))

    doc.build(story)
    print(f"[Успешно] База знаний собрана в файл: {pdf_path} (Всего файлов: {len(md_files)})")

if __name__ == "__main__":
    build_pdf()
