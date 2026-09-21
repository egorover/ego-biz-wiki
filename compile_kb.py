import glob
import html
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import yaml
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

SUBMISSION_DIR = Path("submission")
KNOWLEDGE_BASE_DIR = Path("knowledge_base")
EVALUATION_DATASET_PATH = Path("evaluation/dataset.yaml")

WINDOWS_FONT_PATH = Path(
    os.environ.get("WINDIR", r"C:\Windows")
) / "Fonts" / "arial.ttf"

if WINDOWS_FONT_PATH.exists():
    pdfmetrics.registerFont(TTFont("ArialCustom", str(WINDOWS_FONT_PATH)))
    FONT_NAME = "ArialCustom"
else:
    FONT_NAME = "Helvetica"


def create_styles() -> dict[str, ParagraphStyle]:
    """Create shared PDF styles."""
    return {
        "title": ParagraphStyle(
            "TitleStyle",
            fontName=FONT_NAME,
            fontSize=28,
            leading=34,
            alignment=1,
            spaceAfter=15,
        ),
        "subtitle": ParagraphStyle(
            "SubTitleStyle",
            fontName=FONT_NAME,
            fontSize=14,
            leading=18,
            alignment=1,
            spaceAfter=30,
            textColor=colors.gray,
        ),
        "h1": ParagraphStyle(
            "H1Style",
            fontName=FONT_NAME,
            fontSize=20,
            leading=24,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor("#1A365D"),
        ),
        "h2": ParagraphStyle(
            "H2Style",
            fontName=FONT_NAME,
            fontSize=14,
            leading=18,
            spaceBefore=10,
            spaceAfter=6,
            textColor=colors.HexColor("#2B6CB0"),
        ),
        "h3": ParagraphStyle(
            "H3Style",
            fontName=FONT_NAME,
            fontSize=11,
            leading=15,
            spaceBefore=8,
            spaceAfter=5,
            textColor=colors.HexColor("#2B6CB0"),
        ),
        "body": ParagraphStyle(
            "BodyStyle",
            fontName=FONT_NAME,
            fontSize=10,
            leading=14,
            spaceAfter=8,
        ),
        "meta": ParagraphStyle(
            "MetaStyle",
            fontName=FONT_NAME,
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#4A5568"),
            spaceAfter=5,
        ),
        "case_id": ParagraphStyle(
            "CaseIdStyle",
            fontName=FONT_NAME,
            fontSize=11,
            leading=14,
            spaceBefore=10,
            spaceAfter=5,
            textColor=colors.HexColor("#1A365D"),
        ),
        "small": ParagraphStyle(
            "SmallStyle",
            fontName=FONT_NAME,
            fontSize=8.5,
            leading=11,
            spaceAfter=4,
        ),
    }


def add_footer(canvas, doc) -> None:
    """Add page number to the PDF footer."""
    canvas.saveState()
    canvas.setFont(FONT_NAME, 8)
    canvas.setFillColor(colors.HexColor("#718096"))
    canvas.drawCentredString(
        doc.pagesize[0] / 2,
        24,
        f"EgoBiz Wiki • Page {doc.page}",
    )
    canvas.restoreState()


def escape_text(value: object) -> str:
    """Escape text for ReportLab Paragraph markup."""
    return html.escape(str(value))


def build_knowledge_base_pdf() -> None:
    """Build a PDF artifact from all Markdown knowledge-base documents."""
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)

    pdf_path = SUBMISSION_DIR / "knowledge_base.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    styles = create_styles()

    story = [
        Spacer(1, 150),
        Paragraph("<b>EgoBiz Wiki</b>", styles["title"]),
        Paragraph("Corporate Knowledge Base", styles["subtitle"]),
        Spacer(1, 20),
        Paragraph("<b>Demo Company:</b> EgoTech Solutions", styles["body"]),
        Paragraph(
            f"<b>Date:</b> {datetime.now().strftime('%d.%m.%Y')}",
            styles["body"],
        ),
        Paragraph(
            "<b>Version:</b> 1.0 (Artifact Submission)",
            styles["body"],
        ),
        PageBreak(),
        Paragraph("Table of Contents", styles["h1"]),
        Spacer(1, 10),
    ]

    md_files = sorted(KNOWLEDGE_BASE_DIR.glob("**/*.md"))
    categories: dict[str, list[str]] = defaultdict(list)

    for file_path in md_files:
        rel_path = file_path.relative_to(KNOWLEDGE_BASE_DIR)
        category = str(rel_path.parent)
        title = file_path.stem

        with file_path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("# "):
                    title = line[2:].strip()
                    break

        categories[category].append(title)

    for category, titles in categories.items():
        story.append(
            Paragraph(
                f"<b>Раздел: {escape_text(category)}</b>",
                styles["h2"],
            )
        )
        for title in titles:
            story.append(
                Paragraph(
                    f"• {escape_text(title)}",
                    styles["body"],
                )
            )

    story.append(PageBreak())

    for file_path in md_files:
        rel_path = file_path.relative_to(KNOWLEDGE_BASE_DIR)
        category = str(rel_path.parent)

        story.append(
            Paragraph(
                f"Категория: {escape_text(category)}",
                styles["meta"],
            )
        )
        story.append(
            Paragraph(
                f"Источник: {escape_text(rel_path)}",
                styles["meta"],
            )
        )

        with file_path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                if line.startswith("# "):
                    story.append(
                        Paragraph(
                            escape_text(line[2:]),
                            styles["h1"],
                        )
                    )
                elif line.startswith("## "):
                    story.append(
                        Paragraph(
                            escape_text(line[3:]),
                            styles["h2"],
                        )
                    )
                else:
                    story.append(
                        Paragraph(
                            escape_text(line).replace(
                                "**",
                                "<b>",
                                1,
                            ).replace(
                                "**",
                                "</b>",
                                1,
                            ),
                            styles["body"],
                        )
                    )

        story.append(Spacer(1, 15))
        story.append(
            HRFlowable(
                width="100%",
                thickness=1,
                color=colors.lightgrey,
                spaceAfter=20,
            )
        )

    story.append(PageBreak())
    story.append(Paragraph("Technical Summary", styles["h1"]))
    story.append(
        Paragraph(
            f"<b>Documents Processed:</b> {len(md_files)}",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "<b>Format:</b> Markdown source converted to PDF",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            f"<b>Categories Count:</b> {len(categories)}",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "<b>Purpose:</b> Source knowledge base for the EgoBiz Wiki RAG MVP.",
            styles["body"],
        )
    )

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)

    if len(md_files) != 23:
        raise ValueError(
            f"Expected 23 knowledge-base documents, found {len(md_files)}."
        )

    print(
        "[Успешно] База знаний собрана: "
        f"{pdf_path} (Всего файлов: {len(md_files)})"
    )


def build_evaluation_dataset_pdf() -> None:
    """Build a PDF artifact from the formal evaluation dataset."""
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)

    with EVALUATION_DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = yaml.safe_load(file)

    cases = dataset["cases"]
    pdf_path = SUBMISSION_DIR / "evaluation_dataset.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    styles = create_styles()

    story = [
        Spacer(1, 130),
        Paragraph("<b>EgoBiz Wiki</b>", styles["title"]),
        Paragraph("Formal Evaluation Dataset", styles["subtitle"]),
        Spacer(1, 20),
        Paragraph(
            "<b>Purpose:</b> Evaluation of retrieval, RAG, fallback, "
            "source attribution and typical usage scenarios.",
            styles["body"],
        ),
        Paragraph(
            f"<b>Dataset Version:</b> {escape_text(dataset['version'])}",
            styles["body"],
        ),
        Paragraph(
            f"<b>Evaluation Cases:</b> {len(cases)}",
            styles["body"],
        ),
        Paragraph(
            f"<b>Date:</b> {datetime.now().strftime('%d.%m.%Y')}",
            styles["body"],
        ),
        PageBreak(),
        Paragraph("Dataset Overview", styles["h1"]),
        Paragraph(
            escape_text(dataset["description"]),
            styles["body"],
        ),
        Spacer(1, 10),
    ]

    grouped_cases: dict[str, list[dict]] = defaultdict(list)
    for case in cases:
        grouped_cases[case["category"]].append(case)

    story.append(Paragraph("Case Distribution", styles["h2"]))

    for category, category_cases in grouped_cases.items():
        story.append(
            Paragraph(
                f"• {escape_text(category)}: {len(category_cases)} cases",
                styles["body"],
            )
        )

    story.append(PageBreak())

    for category, category_cases in grouped_cases.items():
        story.append(
            Paragraph(
                f"Category: {escape_text(category)}",
                styles["h1"],
            )
        )

        for case in category_cases:
            story.append(
                Paragraph(
                    f"<b>{escape_text(case['id'])}</b>",
                    styles["case_id"],
                )
            )
            story.append(
                Paragraph(
                    f"<b>Question:</b> {escape_text(case['question'])}",
                    styles["body"],
                )
            )
            story.append(
                Paragraph(
                    "<b>Expected behavior:</b> "
                    f"{escape_text(case['expected_behavior'])}",
                    styles["body"],
                )
            )

            expected_sources = case.get("expected_sources", [])
            story.append(
                Paragraph(
                    "<b>Expected sources:</b>",
                    styles["body"],
                )
            )

            if expected_sources:
                for source in expected_sources:
                    story.append(
                        Paragraph(
                            f"• {escape_text(source)}",
                            styles["small"],
                        )
                    )
            else:
                story.append(
                    Paragraph(
                        "• None",
                        styles["small"],
                    )
                )

            expected_topics = case.get("expected_topics", [])
            story.append(
                Paragraph(
                    "<b>Expected topics:</b>",
                    styles["body"],
                )
            )

            for topic in expected_topics:
                story.append(
                    Paragraph(
                        f"• {escape_text(topic)}",
                        styles["small"],
                    )
                )

            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.7,
                    color=colors.lightgrey,
                    spaceBefore=5,
                    spaceAfter=10,
                )
            )

    story.append(PageBreak())
    story.append(Paragraph("Technical Summary", styles["h1"]))
    story.append(
        Paragraph(
            f"<b>Dataset Version:</b> {escape_text(dataset['version'])}",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            f"<b>Total Cases:</b> {len(cases)}",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            f"<b>Categories:</b> {len(grouped_cases)}",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "<b>Source:</b> evaluation/dataset.yaml",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "<b>Purpose:</b> Reproducible evaluation of the EgoBiz Wiki "
            "RAG MVP behavior.",
            styles["body"],
        )
    )

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)

    if len(cases) != 38:
        raise ValueError(
            f"Expected 38 evaluation cases, found {len(cases)}."
        )

    print(
        "[Успешно] Evaluation dataset собран: "
        f"{pdf_path} (Всего кейсов: {len(cases)})"
    )


def main() -> None:
    """Build all submission PDF artifacts."""
    build_knowledge_base_pdf()
    build_evaluation_dataset_pdf()


if __name__ == "__main__":
    main()