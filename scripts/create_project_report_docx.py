"""Build the Standard and Detailed Candidate Lab Stage-1 reports.

The layout follows the supplied department format: Letter paper, Times New
Roman body text, centred chapter headings, plain black body copy, page numbers
in the footer and a single new page only for chapters and back matter.
"""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from report_content import (
    ABSTRACT,
    ACKNOWLEDGEMENT,
    COLLEGE,
    DEPARTMENT,
    DETAILED_BLOCKS,
    GUIDE,
    GUIDE_DESIGNATION,
    HOD,
    HOD_DESIGNATION,
    PRINCIPAL,
    PROOF_TEXT,
    REFERENCES,
    SHORT_TITLE,
    STANDARD_BLOCKS,
    STUDENTS,
    TITLE,
    YEAR,
)

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "docs" / "report" / "assets"
FIGURES = ASSETS / "figures"

PAGE_WIDTH_CM = 21.59  # US Letter, matching the supplied format document.
PAGE_HEIGHT_CM = 27.94
MARGIN_LEFT_CM = 3.17
MARGIN_RIGHT_CM = 2.54
MARGIN_TOP_CM = 2.54
MARGIN_BOTTOM_CM = 2.54
CONTENT_WIDTH_CM = PAGE_WIDTH_CM - MARGIN_LEFT_CM - MARGIN_RIGHT_CM

BLACK = RGBColor(0x00, 0x00, 0x00)
NAVY = RGBColor(0x1F, 0x38, 0x64)
RED = RGBColor(0xC0, 0x00, 0x00)
COVER_NAVY = RGBColor(0x1F, 0x49, 0x7D)
COVER_RED = RGBColor(0xFF, 0x00, 0x00)
COVER_DARK_NAVY = RGBColor(0x00, 0x1F, 0x5F)
GREY = "D9D9D9"
FONT = "Times New Roman"

OUTPUTS = {
    "standard": ROOT / "docs" / "report" / "Candidate_Lab_Project_Report_Standard.docx",
    "detailed": ROOT / "docs" / "report" / "Candidate_Lab_Project_Report_Detailed.docx",
}


# ---------------------------------------------------------------------------
# Low-level XML and style helpers
# ---------------------------------------------------------------------------


def _set_rfonts(rpr, name: str = FONT) -> None:
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), name)


def _clear_theme_color(rpr) -> None:
    color = rpr.find(qn("w:color"))
    if color is None:
        return
    for attr in ("w:themeColor", "w:themeShade", "w:themeTint"):
        if qn(attr) in color.attrib:
            del color.attrib[qn(attr)]


def style_run(
    run,
    size: float = 12,
    bold: bool = False,
    italic: bool = False,
    color: RGBColor = BLACK,
) -> None:
    run.font.name = FONT
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    _set_rfonts(rpr)
    _clear_theme_color(rpr)


def configure_style(style, size, bold=False, italic=False, color=BLACK) -> None:
    style.font.name = FONT
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.italic = italic
    style.font.color.rgb = color
    rpr = style.element.get_or_add_rPr()
    _set_rfonts(rpr)
    _clear_theme_color(rpr)


def add_rich(
    paragraph,
    text: str,
    size: float = 12,
    bold: bool = False,
    italic: bool = False,
    color: RGBColor = BLACK,
) -> None:
    for part in re.split(r"(\*\*.+?\*\*)", text):
        if not part:
            continue
        part_bold = bold
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            part = part[2:-2]
            part_bold = True
        run = paragraph.add_run(part)
        style_run(run, size=size, bold=part_bold, italic=italic, color=color)


def add_page_field(paragraph) -> None:
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = " PAGE "
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instruction)
    run._r.append(end)
    style_run(run, size=10.5)


def set_page_number_format(section, fmt: str, start: int) -> None:
    sect_pr = section._sectPr
    page_number = sect_pr.find(qn("w:pgNumType"))
    if page_number is None:
        page_number = OxmlElement("w:pgNumType")
        sect_pr.append(page_number)
    page_number.set(qn("w:fmt"), fmt)
    page_number.set(qn("w:start"), str(start))


def configure_section(section) -> None:
    section.page_width = Cm(PAGE_WIDTH_CM)
    section.page_height = Cm(PAGE_HEIGHT_CM)
    section.orientation = 0
    section.top_margin = Cm(MARGIN_TOP_CM)
    section.bottom_margin = Cm(MARGIN_BOTTOM_CM)
    section.left_margin = Cm(MARGIN_LEFT_CM)
    section.right_margin = Cm(MARGIN_RIGHT_CM)
    section.header_distance = Cm(1.27)
    section.footer_distance = Cm(1.27)


def compact_section_break(paragraph) -> None:
    """Make the empty section-break paragraph occupy almost no vertical space."""
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.line_spacing = Pt(1)
    p_pr = paragraph._p.get_or_add_pPr()
    r_pr = p_pr.find(qn("w:rPr"))
    if r_pr is None:
        r_pr = OxmlElement("w:rPr")
        sect_pr = p_pr.find(qn("w:sectPr"))
        if sect_pr is not None:
            sect_pr.addprevious(r_pr)
        else:
            p_pr.append(r_pr)
    for tag in ("w:sz", "w:szCs"):
        size = r_pr.find(qn(tag))
        if size is None:
            size = OxmlElement(tag)
            r_pr.append(size)
        size.set(qn("w:val"), "2")


def add_toc_field(doc, levels: str = "1-2") -> None:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.line_spacing = 1.0
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    begin.set(qn("w:dirty"), "true")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = f' TOC \\o "{levels}" \\h \\z \\u '
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = "Update the field to refresh the table of contents."
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instruction)
    run._r.append(separate)
    run._r.append(placeholder)
    run._r.append(end)


def enable_field_updates(doc) -> None:
    settings = doc.settings.element
    if settings.find(qn("w:updateFields")) is None:
        update = OxmlElement("w:updateFields")
        update.set(qn("w:val"), "true")
        settings.append(update)


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shading = tc_pr.find(qn("w:shd"))
    if shading is None:
        shading = OxmlElement("w:shd")
        tc_pr.append(shading)
    shading.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=30, start=70, bottom=30, end=70) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    margins = tc_pr.find(qn("w:tcMar"))
    if margins is None:
        margins = OxmlElement("w:tcMar")
        tc_pr.append(margins)
    for tag, value in (
        ("w:top", top),
        ("w:start", start),
        ("w:bottom", bottom),
        ("w:end", end),
    ):
        element = margins.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            margins.append(element)
        element.set(qn("w:w"), str(value))
        element.set(qn("w:type"), "dxa")


def set_table_borders(table, color="808080", size=4) -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), str(size))
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)


def remove_table_borders(table) -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "nil")


def _fixed_table_layout(table) -> None:
    tbl_pr = table._tbl.tblPr
    layout = tbl_pr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")


def _repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    tr_pr.append(header)


def _cant_split(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    no_split = OxmlElement("w:cantSplit")
    no_split.set(qn("w:val"), "true")
    tr_pr.append(no_split)


# ---------------------------------------------------------------------------
# Document styles and paragraph helpers
# ---------------------------------------------------------------------------


def configure_styles(doc) -> None:
    normal = doc.styles["Normal"]
    configure_style(normal, 12)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(4)
    normal.paragraph_format.widow_control = True

    heading_specs = {
        "Heading 1": (16, True, WD_ALIGN_PARAGRAPH.CENTER, 0, 18),
        "Heading 2": (14, True, WD_ALIGN_PARAGRAPH.LEFT, 12, 6),
        "Heading 3": (12.5, True, WD_ALIGN_PARAGRAPH.LEFT, 10, 4),
    }
    for name, (size, bold, alignment, before, after) in heading_specs.items():
        style = doc.styles[name]
        configure_style(style, size, bold=bold)
        style.paragraph_format.alignment = alignment
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.line_spacing = 1.0
        style.paragraph_format.page_break_before = name == "Heading 1"

    caption = doc.styles["Caption"]
    configure_style(caption, 10, italic=True)
    caption.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption.paragraph_format.space_before = Pt(3)
    caption.paragraph_format.space_after = Pt(6)
    caption.paragraph_format.line_spacing = 1.0

    table_caption = doc.styles.add_style("TableCaption", 1)
    table_caption.base_style = doc.styles["Normal"]
    configure_style(table_caption, 10, bold=True)
    table_caption.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    table_caption.paragraph_format.space_before = Pt(6)
    table_caption.paragraph_format.space_after = Pt(3)
    table_caption.paragraph_format.keep_with_next = True
    table_caption.paragraph_format.line_spacing = 1.0

    front_heading = doc.styles.add_style("FrontHeading", 1)
    front_heading.base_style = doc.styles["Normal"]
    configure_style(front_heading, 14, bold=True)
    front_heading.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    front_heading.paragraph_format.space_before = Pt(0)
    front_heading.paragraph_format.space_after = Pt(12)
    front_heading.paragraph_format.keep_with_next = True
    front_heading.paragraph_format.line_spacing = 1.0

    # TOC entries use Word's built-in toc 1/toc 2 styles; the export script
    # compacts those styles after the field is refreshed.


def add_chapter(doc, number: int, title: str, first: bool = False) -> None:
    paragraph = doc.add_paragraph(style="Heading 1")
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.page_break_before = not first
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(16)
    add_rich(paragraph, f"CHAPTER {number}", size=16, bold=True)
    add_rich(paragraph, "\n" + title.upper(), size=16, bold=True)


def add_section_heading(doc, text: str) -> None:
    paragraph = doc.add_paragraph(style="Heading 2")
    add_rich(paragraph, text, size=14, bold=True)


def add_subsection_heading(doc, text: str) -> None:
    paragraph = doc.add_paragraph(style="Heading 3")
    add_rich(paragraph, text, size=12.5, bold=True)


def add_front_heading(doc, text: str) -> None:
    paragraph = doc.add_paragraph(style="FrontHeading")
    add_rich(paragraph, text, size=14, bold=True)


def add_body(
    doc,
    text: str,
    after: float = 4,
    line_spacing: float = 1.5,
    alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
    size: float = 12,
    keep_with_next: bool = False,
) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = alignment
    paragraph.paragraph_format.line_spacing = line_spacing
    paragraph.paragraph_format.space_after = Pt(after)
    paragraph.paragraph_format.widow_control = True
    paragraph.paragraph_format.keep_with_next = keep_with_next
    add_rich(paragraph, text, size=size)


def add_bullets(doc, items) -> None:
    for marker, text in items:
        paragraph = doc.add_paragraph()
        paragraph.paragraph_format.left_indent = Cm(1.0)
        paragraph.paragraph_format.first_line_indent = Cm(-1.0)
        paragraph.paragraph_format.line_spacing = 1.5
        paragraph.paragraph_format.space_after = Pt(4)
        paragraph.paragraph_format.tab_stops.add_tab_stop(Cm(1.0))
        add_rich(paragraph, f"{marker}\t{text}", size=12)


def add_formula(doc, text: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(4)
    paragraph.paragraph_format.space_after = Pt(6)
    paragraph.paragraph_format.line_spacing = 1.15
    add_rich(paragraph, text, size=12, bold=True)


def add_table(doc, caption: str, headers, rows, widths, font_size: float = 9.2) -> None:
    cap = doc.add_paragraph(style="TableCaption")
    add_rich(cap, caption, size=10, bold=True)

    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.allow_autofit = False
    _fixed_table_layout(table)

    total = sum(widths)
    scaled = [width * CONTENT_WIDTH_CM / total for width in widths]
    for index, width in enumerate(scaled):
        table.columns[index].width = Cm(width)
        for cell in table.columns[index].cells:
            cell.width = Cm(width)
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:type"), "dxa")
    tbl_w.set(qn("w:w"), str(int(CONTENT_WIDTH_CM * 567)))

    header_row = table.rows[0]
    _repeat_header(header_row)
    _cant_split(header_row)
    for index, value in enumerate(headers):
        cell = header_row.cells[index]
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_shading(cell, GREY)
        set_cell_margins(cell)
        paragraph = cell.paragraphs[0]
        paragraph.paragraph_format.space_before = Pt(1)
        paragraph.paragraph_format.space_after = Pt(1)
        paragraph.paragraph_format.line_spacing = 1.0
        add_rich(paragraph, value, size=font_size, bold=True)

    for row_values in rows:
        row = table.add_row()
        _cant_split(row)
        for index, value in enumerate(row_values):
            cell = row.cells[index]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell)
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_before = Pt(1)
            paragraph.paragraph_format.space_after = Pt(1)
            paragraph.paragraph_format.line_spacing = 1.0
            add_rich(paragraph, value, size=font_size)

    set_table_borders(table)
    for row in table.rows[:-1]:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.keep_with_next = True
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(0)
    spacer.paragraph_format.line_spacing = 0.6


def add_figure(
    doc,
    filename: str,
    caption: str,
    max_width_cm: float,
    max_height_cm: float,
) -> None:
    path = FIGURES / filename
    with Image.open(path) as image:
        width_px, height_px = image.size

    width = min(max_width_cm, CONTENT_WIDTH_CM)
    height = width * height_px / width_px
    if height > max_height_cm:
        height = max_height_cm
        width = height * width_px / height_px
    width = min(width, CONTENT_WIDTH_CM)

    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(4)
    paragraph.paragraph_format.space_after = Pt(2)
    paragraph.paragraph_format.keep_with_next = True
    paragraph.add_run().add_picture(str(path), width=Cm(width))

    cap = doc.add_paragraph(style="Caption")
    add_rich(cap, caption, size=10, italic=True)


# ---------------------------------------------------------------------------
# Front matter
# ---------------------------------------------------------------------------


COVER_TITLE_LINES = (
    "CANDIDATE LAB: AN EXPLAINABLE AL FRAMEWORK",
    "FOR FAIR AND OBJECTIVE TALENT ACQUISITION",
)
assert " ".join(COVER_TITLE_LINES) == TITLE, "Cover title lines must match TITLE"


def cover_line(doc, segments, before: float = 0, after: float = 0) -> None:
    """Add one centred cover line.

    ``segments`` is a sequence of ``(text, size, colour, bold, italic)`` so a
    single line can mix colours and weights exactly as the reference does.
    """
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(before)
    paragraph.paragraph_format.space_after = Pt(after)
    paragraph.paragraph_format.line_spacing = 1.0
    paragraph.paragraph_format.widow_control = False
    for text, size, color, bold, italic in segments:
        run = paragraph.add_run(text)
        style_run(run, size=size, bold=bold, italic=italic, color=color)


def add_cover(doc) -> None:
    cover_line(
        doc,
        [
            ("A Project", 14, BLACK, True, True),
            (" Stage-1 Report", 14, COVER_NAVY, True, True),
        ],
        before=25.41,
    )
    cover_line(doc, [("On", 14, BLACK, True, True)], before=11.12)
    cover_line(
        doc, [(COVER_TITLE_LINES[0], 14, COVER_RED, True, False)], before=9.22
    )
    cover_line(
        doc, [(COVER_TITLE_LINES[1], 14, COVER_RED, True, False)], before=0.02
    )
    cover_line(
        doc,
        [
            (
                "Submitted In partial fulfilment for the award of the Degree of",
                14,
                COVER_NAVY,
                True,
                True,
            )
        ],
        before=13.20,
    )
    cover_line(
        doc, [("BACHELOR OF TECHNOLOGY", 14, COVER_RED, True, False)], before=13.32
    )
    cover_line(doc, [("In", 14, BLACK, True, True)], before=0.12)
    cover_line(
        doc,
        [("COMPUTER SCIENCE & ENGINEERING", 14, COVER_RED, True, False)],
        before=11.02,
    )
    cover_line(
        doc,
        [("(Artificial Intelligence & Machine Learning)", 14, COVER_RED, True, False)],
        before=11.02,
    )
    cover_line(
        doc,
        [("b", 16, BLACK, True, True), ("y", 13, BLACK, True, True)],
        before=9.53,
    )
    name_spacing = (9.28, 9.52, 9.42, 9.52)
    for (name, roll), before in zip(STUDENTS, name_spacing):
        cover_line(
            doc,
            [(f"{name.upper()} ({roll})", 14, COVER_RED, True, True)],
            before=before,
        )
    cover_line(
        doc, [("Under the guidance of", 12, COVER_NAVY, True, False)], before=25.62
    )
    cover_line(doc, [(GUIDE, 14, COVER_RED, False, False)], before=9.20)
    cover_line(doc, [(GUIDE_DESIGNATION, 14, COVER_RED, False, False)], before=9.22)

    logo = doc.add_paragraph()
    logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    logo.paragraph_format.space_before = Pt(10.29)
    logo.paragraph_format.space_after = Pt(0)
    logo.paragraph_format.line_spacing = 1.0
    logo.add_run().add_picture(str(ASSETS / "image1.jpeg"), width=Cm(2.55))

    cover_line(
        doc,
        [("DEPARTMENT OF " + DEPARTMENT, 12, BLACK, True, False)],
        before=13.46,
    )
    cover_line(doc, [(COLLEGE, 16, COVER_RED, True, False)], before=13.81)
    cover_line(
        doc,
        [("(An Autonomous Institution)", 16, COVER_RED, False, False)],
        before=0.14,
    )
    cover_line(
        doc,
        [
            (
                "Approved by AICTE, Accredited by NAAC, NBA & permanently Affiliated to JNTUH",
                12,
                COVER_DARK_NAVY,
                True,
                False,
            )
        ],
        before=10.81,
    )
    cover_line(doc, [(YEAR, 12, BLACK, True, False)], before=12.90)


def add_certificate(doc) -> None:
    banner = doc.add_paragraph()
    banner.alignment = WD_ALIGN_PARAGRAPH.CENTER
    banner.paragraph_format.space_before = Pt(0)
    banner.paragraph_format.space_after = Pt(24)
    banner.add_run().add_picture(str(ASSETS / "image2.jpeg"), width=Cm(12.6))

    add_front_heading(doc, "CERTIFICATE")
    certificate = (
        "This is to certify that the Project Stage-1 report entitled **" + TITLE + "** "
        "submitted by **Deekshith Alle (23911A6672), Sirivennala Kammari (23911A6698), "
        "Rizwana Mohammad (23911A66A9) and Harshavardhan Dyavanapelli (24915A6608)** to "
        "Vidya Jyothi Institute of Technology, Hyderabad, in partial fulfillment for the award "
        "of the degree of **B.Tech CSE (AI&ML)** is a bonafide record of project work carried "
        "out by them under my supervision. The contents of this report, in full or in parts, "
        "have not been submitted to any other Institution or University for the award of any "
        "degree."
    )
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.line_spacing = 1.5
    paragraph.paragraph_format.space_after = Pt(0)
    add_rich(paragraph, certificate, size=12)

    signature_space = doc.add_paragraph()
    signature_space.paragraph_format.space_before = Pt(110)
    signature_space.paragraph_format.space_after = Pt(0)

    signature_table = doc.add_table(rows=1, cols=2)
    signature_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    signature_table.autofit = False
    signature_table.allow_autofit = False
    remove_table_borders(signature_table)
    for cell, lines in (
        (signature_table.rows[0].cells[0], ("Signature of Supervisor", GUIDE, GUIDE_DESIGNATION, "Department of CSE (AI&ML)")),
        (signature_table.rows[0].cells[1], ("Signature of HOD", HOD, HOD_DESIGNATION, "Department of CSE (AI&ML)")),
    ):
        cell.width = Cm(CONTENT_WIDTH_CM / 2)
        paragraph = cell.paragraphs[0]
        paragraph.paragraph_format.space_after = Pt(2)
        paragraph.paragraph_format.line_spacing = 1.0
        add_rich(paragraph, lines[0], size=11.5, bold=True)
        for line in lines[1:]:
            paragraph = cell.add_paragraph()
            paragraph.paragraph_format.space_after = Pt(2)
            paragraph.paragraph_format.line_spacing = 1.0
            add_rich(paragraph, line, size=11.5, bold=line != lines[-1])


def add_acknowledgement(doc) -> None:
    add_front_heading(doc, "ACKNOWLEDGEMENT")
    for text in ACKNOWLEDGEMENT:
        add_body(doc, text, after=8, line_spacing=1.4)
    for _ in range(2):
        spacer = doc.add_paragraph()
        spacer.paragraph_format.space_after = Pt(0)
        spacer.paragraph_format.line_spacing = 1.0
    by = doc.add_paragraph()
    by.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    by.paragraph_format.space_after = Pt(6)
    add_rich(by, "By", size=12)
    for name, roll in STUDENTS:
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        paragraph.paragraph_format.space_after = Pt(2)
        paragraph.paragraph_format.line_spacing = 1.0
        add_rich(paragraph, f"{name}  ({roll})", size=12)


def add_abstract(doc) -> None:
    add_front_heading(doc, "ABSTRACT")
    for text in ABSTRACT:
        add_body(doc, text, after=8, line_spacing=1.15)


def add_toc(doc, levels: str) -> None:
    add_front_heading(doc, "TABLE OF CONTENTS")
    add_toc_field(doc, levels)


# ---------------------------------------------------------------------------
# Body and back matter
# ---------------------------------------------------------------------------


def add_references(doc) -> None:
    heading = doc.add_paragraph(style="Heading 1")
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    heading.paragraph_format.page_break_before = True
    add_rich(heading, "REFERENCES", size=16, bold=True)
    intro = (
        "The following sources informed the problem framing, the matching baseline, the document "
        "processing pipeline and the audit design. Web documentation was accessed in November 2026."
    )
    add_body(doc, intro, after=8, line_spacing=1.15, size=11)
    for reference in REFERENCES:
        paragraph = doc.add_paragraph()
        paragraph.paragraph_format.left_indent = Cm(0.9)
        paragraph.paragraph_format.first_line_indent = Cm(-0.9)
        paragraph.paragraph_format.space_after = Pt(5)
        paragraph.paragraph_format.line_spacing = 1.15
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        add_rich(paragraph, reference, size=11)


def add_proof(doc) -> None:
    heading = doc.add_paragraph(style="Heading 1")
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    heading.paragraph_format.page_break_before = True
    add_rich(heading, "PROOF OF PUBLICATION", size=16, bold=True)
    add_body(doc, PROOF_TEXT, after=12, line_spacing=1.3)

    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.allow_autofit = False
    set_table_borders(table, color="808080", size=6)
    cell = table.rows[0].cells[0]
    cell.width = Cm(CONTENT_WIDTH_CM)
    set_cell_shading(cell, "F2F2F2")
    set_cell_margins(cell, top=140, start=180, bottom=140, end=180)
    proof_lines = [
        ("Publication status", "Not yet published or communicated"),
        ("Title", TITLE),
        ("Authors", ", ".join(f"{name} ({roll})" for name, roll in STUDENTS)),
        ("Journal / conference", "To be inserted after acceptance"),
        ("DOI / proof reference", "To be inserted after publication"),
    ]
    first = True
    for label, value in proof_lines:
        paragraph = cell.paragraphs[0] if first else cell.add_paragraph()
        first = False
        paragraph.paragraph_format.space_after = Pt(6)
        paragraph.paragraph_format.line_spacing = 1.15
        add_rich(paragraph, f"**{label}:** {value}", size=11)

    note = doc.add_paragraph()
    note.paragraph_format.space_before = Pt(12)
    note.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    add_rich(
        note,
        "The project team will replace this page with authentic proof if a publication is produced. "
        "The absence of a publication is not treated as a failure of the Stage-1 work; the report "
        "documents the implemented prototype and its verification instead.",
        size=10.5,
        italic=True,
    )


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def render_blocks(doc, blocks) -> None:
    first_chapter = True
    for block in blocks:
        kind = block[0]
        if kind == "chapter":
            add_chapter(doc, block[1], block[2], first=first_chapter)
            first_chapter = False
        elif kind == "section":
            add_section_heading(doc, block[1])
        elif kind == "subsection":
            add_subsection_heading(doc, block[1])
        elif kind == "body":
            add_body(doc, block[1])
        elif kind == "bullets":
            add_bullets(doc, block[1])
        elif kind == "formula":
            add_formula(doc, block[1])
        elif kind == "table":
            add_table(doc, block[1], block[2], block[3], block[4])
        elif kind == "figure":
            add_figure(doc, block[1], block[2], block[3], block[4])
        else:
            raise ValueError(f"Unknown report block: {kind}")


def build(variant: str) -> Path:
    doc = Document()
    configure_section(doc.sections[0])
    configure_styles(doc)
    enable_field_updates(doc)

    doc.styles["Normal"].paragraph_format.line_spacing = 1.5
    doc.core_properties.title = f"{SHORT_TITLE} - Project Stage-1 Report ({variant.title()} edition)"
    doc.core_properties.author = ", ".join(name for name, _ in STUDENTS)
    doc.core_properties.subject = TITLE
    doc.core_properties.comments = f"Project Stage-1 report, Department of CSE (AI&ML), VJIT ({variant} edition)."

    # Cover: no footer, and a smaller bottom margin so the year line can sit at
    # the reference position without spilling onto a second page.
    add_cover(doc)
    doc.sections[0].bottom_margin = Cm(0.9)

    # Front matter: lower-case Roman numerals starting at ii.
    front = doc.add_section(WD_SECTION.NEW_PAGE)
    compact_section_break(doc.paragraphs[-1])
    configure_section(front)
    front.footer.is_linked_to_previous = False
    front.footer.paragraphs[0].text = ""
    front.footer.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_page_field(front.footer.paragraphs[0])
    set_page_number_format(front, "lowerRoman", 2)

    add_certificate(doc)
    doc.add_page_break()
    add_acknowledgement(doc)
    doc.add_page_break()
    add_abstract(doc)
    doc.add_page_break()
    add_toc(doc, "1-2")

    # Body: decimal numbering starting at 1.
    body = doc.add_section(WD_SECTION.NEW_PAGE)
    configure_section(body)
    body.footer.is_linked_to_previous = False
    body.footer.paragraphs[0].text = ""
    body.footer.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_page_field(body.footer.paragraphs[0])
    set_page_number_format(body, "decimal", 1)

    blocks = DETAILED_BLOCKS if variant == "detailed" else STANDARD_BLOCKS
    render_blocks(doc, blocks)
    add_references(doc)
    add_proof(doc)

    output = OUTPUTS[variant]
    doc.save(output)
    print(f"Wrote {output}")
    print(f"Paragraphs: {len(doc.paragraphs)}, tables: {len(doc.tables)}")
    return output


def main() -> None:
    for variant in ("standard", "detailed"):
        build(variant)


if __name__ == "__main__":
    main()
