"""Build the Version 2 Standard and Detailed Candidate Lab reports.

Version 2 reuses the frozen front matter and all layout helpers from
``create_project_report_docx`` but swaps in the expanded body content from
``report_content_v2``.  The originals are left untouched so the reviewed
Version 1 files remain available.
"""
from __future__ import annotations

from pathlib import Path

from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

import create_project_report_docx as builder
import report_content_v2 as content

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "docs" / "report"

OUTPUTS = {
    "standard": REPORT_DIR / "Candidate_Lab_Project_Report_Standard_V2.docx",
    "detailed": REPORT_DIR / "Candidate_Lab_Project_Report_Detailed_V2.docx",
}


def add_back_matter(doc) -> None:
    """Render references and the publication record on one compact page."""
    heading = doc.add_paragraph(style="Heading 1")
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    heading.paragraph_format.page_break_before = True
    builder.add_rich(heading, "REFERENCES", size=16, bold=True)

    intro = (
        "The following sources informed the problem framing, the matching baseline, the document "
        "processing pipeline and the audit design. Web documentation was accessed in November 2026."
    )
    builder.add_body(doc, intro, after=6, line_spacing=1.0, size=10)

    for reference in builder.REFERENCES:
        paragraph = doc.add_paragraph()
        paragraph.paragraph_format.left_indent = Cm(0.75)
        paragraph.paragraph_format.first_line_indent = Cm(-0.75)
        paragraph.paragraph_format.space_after = Pt(3)
        paragraph.paragraph_format.line_spacing = 1.0
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        builder.add_rich(paragraph, reference, size=9.5)

    proof_heading = doc.add_paragraph(style="Heading 1")
    proof_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    proof_heading.paragraph_format.page_break_before = False
    proof_heading.paragraph_format.space_before = Pt(14)
    builder.add_rich(proof_heading, "PROOF OF PUBLICATION", size=14, bold=True)

    builder.add_body(doc, builder.PROOF_TEXT, after=6, line_spacing=1.0, size=9.5)

    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.allow_autofit = False
    builder.set_table_borders(table, color="808080", size=6)
    cell = table.rows[0].cells[0]
    cell.width = Cm(builder.CONTENT_WIDTH_CM)
    builder.set_cell_shading(cell, "F2F2F2")
    builder.set_cell_margins(cell, top=80, start=120, bottom=80, end=120)
    proof_lines = [
        ("Publication status", "Not yet published or communicated"),
        ("Title", builder.TITLE),
        ("Authors", ", ".join(f"{name} ({roll})" for name, roll in builder.STUDENTS)),
        ("Journal / conference", "To be inserted after acceptance"),
        ("DOI / proof reference", "To be inserted after publication"),
    ]
    first = True
    for label, value in proof_lines:
        paragraph = cell.paragraphs[0] if first else cell.add_paragraph()
        first = False
        paragraph.paragraph_format.space_after = Pt(3)
        paragraph.paragraph_format.line_spacing = 1.0
        builder.add_rich(paragraph, f"**{label}:** {value}", size=9)

    note = doc.add_paragraph()
    note.paragraph_format.space_before = Pt(8)
    note.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    builder.add_rich(
        note,
        "The project team will replace this page with authentic proof if a publication is produced. "
        "The absence of a publication is not treated as a failure of the Stage-1 work; the report "
        "documents the implemented prototype and its verification instead.",
        size=8.5,
        italic=True,
    )


def apply_content() -> None:
    for name in (
        "STANDARD_BLOCKS",
        "DETAILED_BLOCKS",
        "REFERENCES",
        "PROOF_TEXT",
    ):
        setattr(builder, name, getattr(content, name))


def main() -> None:
    apply_content()
    builder.OUTPUTS = OUTPUTS
    builder.TIGHT_FIGURE_SPACING = True
    builder.add_references = add_back_matter
    builder.add_proof = lambda doc: None
    for variant in ("standard", "detailed"):
        builder.build(variant)


if __name__ == "__main__":
    main()
