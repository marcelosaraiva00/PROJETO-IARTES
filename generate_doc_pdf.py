"""
Gera PDF da documentação acadêmica (DOCUMENTACAO_IA_ORDENACAO_TESTES.md).
Requer: pip install reportlab
Uso: python generate_doc_pdf.py
"""
import io
import re
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def escape_xml(s: str) -> str:
    """Escapa caracteres para uso em tags ReportLab."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def md_to_reportlab(s: str) -> str:
    """Converte markdown simples para tags ReportLab (bold, italic, code)."""
    # **text** -> <b>text</b>
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    # *text* (não entre **) -> <i>text</i>; evita conflito com listas *
    s = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', s)
    # `code` -> monospace via font (ReportLab usa size, face)
    s = re.sub(r'`([^`]+)`', r'<font face="Courier" size="9">\1</font>', s)
    s = escape_xml(s)
    # Restaurar tags que escapamos (ReportLab exige > e < válidos)
    s = s.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    s = s.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
    s = s.replace('&lt;font face="Courier" size="9"&gt;', '<font face="Courier" size="9">')
    s = s.replace("&lt;/font&gt;", "</font>")
    return s


def build_story(md_path: Path):
    """Lê o Markdown e retorna lista de flowables para o PDF."""
    text = md_path.read_text(encoding="utf-8")
    lines = text.split("\n")
    story = []
    in_code = False
    code_lines = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#1e40af"),
        spaceAfter=12,
        alignment=1,
    )
    h1_style = ParagraphStyle(
        "DocH1",
        parent=styles["Heading1"],
        fontSize=14,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=14,
        spaceAfter=8,
    )
    h2_style = ParagraphStyle(
        "DocH2",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=6,
    )
    bullet_style = ParagraphStyle(
        "DocBullet",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        leftIndent=20,
        spaceAfter=4,
    )
    code_style = ParagraphStyle(
        "DocCode",
        parent=styles["Code"],
        fontSize=8,
        leading=10,
        leftIndent=15,
        rightIndent=15,
        backColor=colors.HexColor("#f1f5f9"),
        spaceAfter=8,
        fontName="Courier",
    )

    i = 0
    while i < len(lines):
        line = lines[i]
        raw = line.strip()

        if raw.startswith("```"):
            if in_code:
                code_text = "\n".join(code_lines)
                story.append(Preformatted(code_text, code_style))
                code_lines = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if raw == "---":
            story.append(Spacer(1, 0.15 * inch))
            i += 1
            continue

        if raw.startswith("# "):
            story.append(Paragraph(md_to_reportlab(raw[2:].strip()), title_style))
            i += 1
            continue

        if raw.startswith("## "):
            story.append(Paragraph(md_to_reportlab(raw[3:].strip()), h1_style))
            i += 1
            continue

        if raw.startswith("### "):
            story.append(Paragraph(md_to_reportlab(raw[4:].strip()), h2_style))
            i += 1
            continue

        if raw.startswith("- ") or raw.startswith("* "):
            content = raw[2:].strip()
            if content:
                story.append(Paragraph("• " + md_to_reportlab(content), bullet_style))
            i += 1
            continue

        if re.match(r"^\d+\.\s", raw):
            content = re.sub(r"^\d+\.\s", "", raw)
            if content:
                story.append(Paragraph(md_to_reportlab(content), bullet_style))
            i += 1
            continue

        if raw:
            story.append(Paragraph(md_to_reportlab(raw), body_style))
        else:
            story.append(Spacer(1, 6))

        i += 1

    if in_code and code_lines:
        story.append(Preformatted("\n".join(code_lines), code_style))

    return story


def main():
    if not REPORTLAB_AVAILABLE:
        print("Erro: reportlab não está instalado. Execute: pip install reportlab")
        return 1

    root = Path(__file__).parent
    md_path = root / "DOCUMENTACAO_IA_ORDENACAO_TESTES.md"
    pdf_path = root / "DOCUMENTACAO_IA_ORDENACAO_TESTES.pdf"

    if not md_path.exists():
        print(f"Arquivo não encontrado: {md_path}")
        return 1

    print("Gerando PDF...")
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50,
    )
    story = build_story(md_path)
    doc.build(story)
    pdf_path.write_bytes(buffer.getvalue())
    print(f"PDF gerado: {pdf_path}")
    return 0


if __name__ == "__main__":
    exit(main())
