"""Optional one-page PDF renderer; use a separate environment with ReportLab/pypdf."""

import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

from pypdf import PdfReader
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate

root = Path(__file__).resolve().parents[1]
output = root / "output/pdf"
output.mkdir(parents=True, exist_ok=True)
source = (root / "docs/FINAL_SUBMISSION_COPY.md").read_text(encoding="utf-8")
blocks = source.strip().split("\n\n")
story = []
styles = {
    "title": ParagraphStyle(
        "title",
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        textColor=HexColor("#143b3a"),
        spaceAfter=9,
    ),
    "sub": ParagraphStyle(
        "sub",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=HexColor("#246b60"),
        spaceAfter=11,
    ),
    "body": ParagraphStyle(
        "body",
        fontName="Helvetica",
        fontSize=10,
        leading=13.2,
        spaceAfter=8,
        textColor=HexColor("#213431"),
    ),
    "source": ParagraphStyle(
        "source",
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        spaceAfter=6,
        textColor=HexColor("#445650"),
    ),
}
for i, block in enumerate(blocks):
    block = block.replace("**", "").replace("# ", "")
    # Explicit linked titles and readable DOI references.
    links = []

    def link(match, links=links):
        links.append((match.group(1), match.group(2)))
        return f"LINKTOKEN{len(links) - 1}END"

    block = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, block)
    block = escape(block).replace("\n", " ")
    for j, (label, url) in enumerate(links):
        label = (
            label
            + " ("
            + url.replace("https://doi.org/", "doi:").replace(
                "https://www.nature.com/articles/", "nature.com/articles/"
            )
            + ")"
        )
        block = block.replace(
            f"LINKTOKEN{j}END", f'<link href="{escape(url)}" color="#246b60">{escape(label)}</link>'
        )
    style = styles[
        "title" if i == 0 else "sub" if i == 1 else "source" if i >= len(blocks) - 2 else "body"
    ]
    story.append(Paragraph(block, style))
pdf = output / "oxyproof-one-page-submission.pdf"


def page(canvas, doc):
    canvas.setStrokeColor(HexColor("#8baea1"))
    canvas.line(42, 37, A4[0] - 42, 37)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(HexColor("#52655d"))
    canvas.drawString(42, 25, "OxyProof | Owner review copy | 20 October 2026 | Not submitted")
    canvas.drawRightString(A4[0] - 42, 25, str(doc.page))


SimpleDocTemplate(
    str(pdf),
    pagesize=A4,
    rightMargin=42,
    leftMargin=42,
    topMargin=35,
    bottomMargin=47,
    title="OxyProof - Scientific Decision Audit",
    author="OxyProof contributors",
).build(story, onFirstPage=page, onLaterPages=page)
reader = PdfReader(pdf)
assert len(reader.pages) == 1, f"Expected 1 page, got {len(reader.pages)}"
text = reader.pages[0].extract_text()
assert "experimental confirmation required" in text and "145 backend" in text
(root / "artifacts/pdf_acceptance.json").write_text(
    json.dumps(
        {
            "path": pdf.relative_to(root).as_posix(),
            "page_count": len(reader.pages),
            "text_extraction": "PASS",
            "visual_review": "PENDING",
            "source": "docs/FINAL_SUBMISSION_COPY.md",
            "renderer": "ReportLab 5.0.1; pypdf 6.21.1; Poppler PNG review required",
        },
        indent=2,
    )
    + "\n"
)
print("PDF_PAGE_COUNT=1", pdf)
