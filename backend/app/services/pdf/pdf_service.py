"""
PDF Generation Service — Professional multi-section PDF using reportlab
"""
from io import BytesIO
from typing import Any, Dict, Optional
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.platypus.tableofcontents import TableOfContents
from loguru import logger

from app.models.project import Project


# ─── Color Palette ───────────────────────────────────────────────────────────
PRIMARY_COLOR = colors.HexColor("#6366F1")      # Indigo
SECONDARY_COLOR = colors.HexColor("#8B5CF6")    # Purple
ACCENT_COLOR = colors.HexColor("#0EA5E9")       # Sky Blue
DARK_BG = colors.HexColor("#1E1B4B")            # Dark Indigo
LIGHT_BG = colors.HexColor("#F8F7FF")           # Very light purple
BORDER_COLOR = colors.HexColor("#E0E7FF")       # Light border
TEXT_DARK = colors.HexColor("#1E293B")          # Dark text
TEXT_MEDIUM = colors.HexColor("#475569")        # Medium text


def _build_styles():
    """Build custom paragraph styles for the PDF."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontSize=28,
        textColor=colors.white,
        spaceAfter=12,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=14,
        textColor=colors.HexColor("#C7D2FE"),
        spaceAfter=6,
        fontName="Helvetica",
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=PRIMARY_COLOR,
        spaceBefore=20,
        spaceAfter=10,
        fontName="Helvetica-Bold",
        borderPad=4,
    ))

    styles.add(ParagraphStyle(
        "SubHeading",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=SECONDARY_COLOR,
        spaceBefore=12,
        spaceAfter=6,
        fontName="Helvetica-Bold",
    ))

    styles.add(ParagraphStyle(
        "BodyText2",
        parent=styles["Normal"],
        fontSize=10,
        textColor=TEXT_DARK,
        spaceAfter=4,
        leading=16,
        alignment=TA_JUSTIFY,
    ))

    styles.add(ParagraphStyle(
        "BulletText",
        parent=styles["Normal"],
        fontSize=10,
        textColor=TEXT_DARK,
        leftIndent=20,
        spaceAfter=3,
        leading=14,
        bulletIndent=10,
    ))

    styles.add(ParagraphStyle(
        "CustomCode",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#374151"),
        backColor=colors.HexColor("#F3F4F6"),
        fontName="Courier",
        borderPad=8,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.white,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontSize=9,
        textColor=TEXT_DARK,
        leading=12,
    ))

    return styles


def _cover_page(story, project: Project, styles):
    """Generate the professional cover page."""
    # Cover background (using a colored table)
    cover_data = [[""]]
    cover_table = Table(cover_data, colWidths=[6.5 * inch], rowHeights=[3 * inch])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_BG),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("DocuForge AI", styles["DocTitle"]))
    story.append(Paragraph("AI-Powered Software Engineering Documentation", styles["DocSubtitle"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY_COLOR))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph(project.title, ParagraphStyle(
        "ProjectTitle", fontSize=22, textColor=TEXT_DARK,
        fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=6
    )))
    story.append(Paragraph(
        "Complete Software Engineering Documentation Package",
        ParagraphStyle("PackageLabel", fontSize=12, textColor=TEXT_MEDIUM,
                       fontName="Helvetica", alignment=TA_CENTER, spaceAfter=20)
    ))

    # Metadata table
    meta_data = [
        ["Domain", project.domain.upper(), "Team Size", f"{project.team_size} Members"],
        ["Timeline", f"{project.timeline_weeks} Weeks", "Generated", datetime.now().strftime("%B %d, %Y")],
    ]
    meta_table = Table(meta_data, colWidths=[1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_BG),
        ("BACKGROUND", (2, 0), (2, -1), LIGHT_BG),
        ("TEXTCOLOR", (0, 0), (0, -1), TEXT_MEDIUM),
        ("TEXTCOLOR", (2, 0), (2, -1), TEXT_MEDIUM),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUND", (0, 0), (-1, -1), [colors.white, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", (0, 0), (-1, -1), [4, 4, 4, 4]),
    ]))

    story.append(meta_table)
    story.append(PageBreak())


def _add_section(story, title: str, styles):
    """Add a formatted section header."""
    story.append(Spacer(1, 0.2 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_COLOR))
    story.append(Paragraph(title, styles["SectionHeading"]))


def _add_table(story, headers: list, rows: list, col_widths=None):
    """Add a professionally styled data table."""
    data = [headers] + rows
    if col_widths is None:
        col_widths = [6.5 * inch / len(headers)] * len(headers)

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_COLOR),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("TEXTCOLOR", (0, 1), (-1, -1), TEXT_DARK),
        ("ROWBACKGROUND", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.3, BORDER_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("WORDWRAP", (0, 0), (-1, -1), True),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.15 * inch))


def generate_project_pdf(project: Project, docs: Dict[str, Any]) -> bytes:
    """
    Generate a complete, professionally formatted PDF for a project.
    Returns the PDF as bytes.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=f"{project.title} - Software Engineering Documentation",
        author="DocuForge AI",
        subject="Software Engineering Documentation Package",
    )

    styles = _build_styles()
    story = []

    # Cover page
    _cover_page(story, project, styles)

    # ─── Requirements ────────────────────────────────────────────────────────
    reqs = docs.get("requirements")
    if reqs:
        _add_section(story, "1. Requirements Analysis", styles)
        story.append(Paragraph(
            f"This section presents the complete requirements specification following IEEE 830 standard.",
            styles["BodyText2"]
        ))

        story.append(Paragraph("1.1 Functional Requirements", styles["SubHeading"]))
        if reqs.get("functional"):
            headers = ["ID", "Title", "Priority", "Description"]
            rows = [
                [r.get("req_id", ""), r.get("title", "")[:40],
                 r.get("priority", "").upper(),
                 r.get("description", "")[:100] + "..."]
                for r in reqs["functional"][:15]
            ]
            _add_table(story, headers, rows, [0.7*inch, 1.5*inch, 0.7*inch, 3.5*inch])

        story.append(Paragraph("1.2 Non-Functional Requirements", styles["SubHeading"]))
        if reqs.get("non_functional"):
            headers = ["ID", "Title", "Category", "Description"]
            rows = [
                [r.get("req_id", ""), r.get("title", "")[:40],
                 r.get("category", ""),
                 r.get("description", "")[:100] + "..."]
                for r in reqs["non_functional"][:10]
            ]
            _add_table(story, headers, rows, [0.7*inch, 1.5*inch, 1.0*inch, 3.2*inch])

    # ─── User Stories ────────────────────────────────────────────────────────
    stories_doc = docs.get("user_stories")
    if stories_doc and stories_doc.get("stories"):
        _add_section(story, "2. User Stories", styles)
        headers = ["ID", "Epic", "As a...", "I want...", "Points", "Sprint"]
        rows = [
            [s.get("story_id", ""), s.get("epic", "")[:20],
             s.get("as_a", "")[:20], s.get("i_want", "")[:50] + "...",
             str(s.get("story_points", 0)), str(s.get("sprint", 1))]
            for s in stories_doc["stories"][:20]
        ]
        _add_table(story, headers, rows,
                   [0.6*inch, 1.0*inch, 0.9*inch, 2.5*inch, 0.5*inch, 0.5*inch])

    # ─── Risk Register ───────────────────────────────────────────────────────
    risk_doc = docs.get("risks")
    if risk_doc and risk_doc.get("risks"):
        _add_section(story, "3. Risk Register", styles)
        headers = ["ID", "Risk Title", "Probability", "Impact", "Level", "Owner"]
        rows = [
            [r.get("risk_id", ""), r.get("title", "")[:50],
             r.get("probability", "").upper(), r.get("impact", "").upper(),
             r.get("risk_level", "").upper(), r.get("owner", "")]
            for r in risk_doc["risks"][:15]
        ]
        _add_table(story, headers, rows,
                   [0.5*inch, 2.0*inch, 0.8*inch, 0.7*inch, 0.7*inch, 1.2*inch])

    # ─── Test Cases ──────────────────────────────────────────────────────────
    test_doc = docs.get("test_cases")
    if test_doc and test_doc.get("test_cases"):
        _add_section(story, "4. Test Cases", styles)
        headers = ["ID", "Type", "Title", "Priority", "Req. ID"]
        rows = [
            [t.get("test_id", ""), t.get("test_type", "").upper(),
             t.get("title", "")[:60], t.get("priority", "").upper(),
             t.get("requirement_id", "-")]
            for t in test_doc["test_cases"][:20]
        ]
        _add_table(story, headers, rows,
                   [0.6*inch, 0.9*inch, 2.8*inch, 0.7*inch, 0.8*inch])

    # ─── Footer ──────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Spacer(1, 2 * inch))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY_COLOR))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        f"Generated by DocuForge AI • {datetime.now().strftime('%B %d, %Y')} • {project.title}",
        ParagraphStyle("Footer", fontSize=10, textColor=TEXT_MEDIUM,
                       fontName="Helvetica", alignment=TA_CENTER)
    ))

    try:
        doc.build(story)
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        raise
