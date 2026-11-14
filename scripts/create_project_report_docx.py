"""Build the Candidate Lab Project Stage-1 report in the supplied format.

The script intentionally keeps the report content in one place so that the
DOCX can be regenerated after verification. Diagrams are pre-rendered PNG
files in report-assets/figures; the official banner and logo are extracted
from the supplied format document.
"""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image
from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import (
    WD_ALIGN_PARAGRAPH,
    WD_LINE_SPACING,
    WD_TAB_ALIGNMENT,
    WD_TAB_LEADER,
)
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "report-assets"
FIGURES = ASSETS / "figures"
OUT_DOCX = ROOT / "Candidate_Lab_Project_Report.docx"

NAVY = RGBColor(0x14, 0x2B, 0x40)
BLUE = RGBColor(0x1F, 0x38, 0x64)
RED = RGBColor(0xC0, 0x00, 0x00)
INK = RGBColor(0x17, 0x25, 0x2E)
MUTED = RGBColor(0x59, 0x59, 0x59)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
PALE_BLUE = "DCE6F1"
PALE_TEAL = "DDEFEA"
PALE_GREY = "F2F5F7"

TITLE = (
    "CANDIDATE LAB: FAIR AND EXPLAINABLE MACHINE LEARNING FOR "
    "AUTOMATED CANDIDATE SELECTION AND SKILL MATCHING"
)
SHORT_TITLE = "Candidate Lab"
STUDENTS = [
    ("Deekshith Alle", "23911A6672"),
    ("Sirivennala Kammari", "23911A6698"),
    ("Rizwana Mohammad", "23911A66A9"),
    ("Harshavardhan Dyavanapelli", "24915A6608"),
]
GUIDE = "Mrs. Y. Uma Mythraye"
GUIDE_DESIGNATION = "Assistant Professor"
HOD = "Dr. N. Anusha"
HOD_DESIGNATION = "Associate Professor"
PRINCIPAL = "Dr. A. Srujana"
COLLEGE = "VIDYA JYOTHI INSTITUTE OF TECHNOLOGY"
DEPARTMENT = "COMPUTER SCIENCE & ENGINEERING (AI&ML)"
YEAR = "2025 – 2026"


# ---------------------------------------------------------------------------
# Low-level formatting helpers
# ---------------------------------------------------------------------------


def force_font(style, name="Times New Roman"):
    style.font.name = name
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), name)


def style_run(run, size=12, bold=False, italic=False, color=INK, name="Times New Roman"):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), name)


def add_rich(paragraph, text, size=12, color=INK, bold=False, italic=False):
    """Add text with **bold** segments, preserving ordinary punctuation."""
    for part in re.split(r"(\*\*.*?\*\*)", text):
        if not part:
            continue
        is_bold = part.startswith("**") and part.endswith("**") and len(part) > 4
        run = paragraph.add_run(part[2:-2] if is_bold else part)
        style_run(run, size=size, bold=bold or is_bold, italic=italic, color=color)


def add_page_field(paragraph, instruction=" PAGE "):
    def field_run(kind, text=""):
        run = paragraph.add_run()
        if kind == "begin":
            element = OxmlElement("w:fldChar")
            element.set(qn("w:fldCharType"), "begin")
        elif kind == "instr":
            element = OxmlElement("w:instrText")
            element.set(qn("xml:space"), "preserve")
            element.text = text
        elif kind == "separate":
            element = OxmlElement("w:fldChar")
            element.set(qn("w:fldCharType"), "separate")
        elif kind == "text":
            element = OxmlElement("w:t")
            element.text = text
        else:
            element = OxmlElement("w:fldChar")
            element.set(qn("w:fldCharType"), "end")
        run._r.append(element)
        style_run(run, size=10, color=MUTED)

    field_run("begin")
    field_run("instr", instruction)
    field_run("separate")
    field_run("text", "1")
    field_run("end")


def set_page_number_format(section, fmt="decimal", start=1):
    sect_pr = section._sectPr
    pg_num = sect_pr.find(qn("w:pgNumType"))
    if pg_num is None:
        pg_num = OxmlElement("w:pgNumType")
        sect_pr.append(pg_num)
    pg_num.set(qn("w:fmt"), fmt)
    pg_num.set(qn("w:start"), str(start))


def clear_page_number_restart(section):
    """Drop a copied pgNumType start value so numbering continues across sections."""
    pg_num = section._sectPr.find(qn("w:pgNumType"))
    if pg_num is not None and pg_num.get(qn("w:start")) is not None:
        del pg_num.attrib[qn("w:start")]


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=100, bottom=80, end=100):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.find(qn("w:tcMar"))
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for tag, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{tag}"))
        if node is None:
            node = OxmlElement(f"w:{tag}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_borders(table, color="A6A6A6", size=4):
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), str(size))
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)
        borders.append(element)
    tbl_pr.append(borders)


def remove_table_borders(table):
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "nil")
        borders.append(element)
    tbl_pr.append(borders)


def add_table(doc, caption, headers, rows, widths_cm, font_size=9.5):
    cap = doc.add_paragraph(style="TableCaption")
    add_rich(cap, caption, size=9.5, color=NAVY, bold=True)
    cap.paragraph_format.keep_with_next = True

    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.allow_autofit = False
    set_table_borders(table)

    header_cells = table.rows[0].cells
    for idx, header in enumerate(headers):
        cell = header_cells[idx]
        cell.width = Cm(widths_cm[idx])
        set_cell_shading(cell, PALE_BLUE)
        set_cell_margins(cell)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        paragraph = cell.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        paragraph.paragraph_format.space_after = Pt(0)
        paragraph.paragraph_format.line_spacing = 1.0
        add_rich(paragraph, header, size=font_size, color=NAVY, bold=True)

    tr_pr = table.rows[0]._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)

    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for idx, value in enumerate(row):
            cell = cells[idx]
            cell.width = Cm(widths_cm[idx])
            set_cell_margins(cell)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if row_index % 2 == 1:
                set_cell_shading(cell, PALE_GREY)
            paragraph = cell.paragraphs[0]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
            paragraph.paragraph_format.space_after = Pt(0)
            paragraph.paragraph_format.line_spacing = 1.0
            add_rich(paragraph, str(value), size=font_size, color=INK)
        tr_pr = table.rows[-1]._tr.get_or_add_trPr()
        cant_split = OxmlElement("w:cantSplit")
        tr_pr.append(cant_split)

    total_width = sum(widths_cm)
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:type"), "dxa")
    tbl_w.set(qn("w:w"), str(int(total_width * 567)))

    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(0)
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.line_spacing = 0.5
    return table


def add_figure(doc, filename, caption, max_width_cm=15.7, max_height_cm=20.6):
    path = FIGURES / filename
    with Image.open(path) as image:
        width_px, height_px = image.size
    width = max_width_cm
    height = width * height_px / width_px
    if height > max_height_cm:
        height = max_height_cm
        width = height * width_px / height_px

    picture_paragraph = doc.add_paragraph()
    picture_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    picture_paragraph.paragraph_format.space_before = Pt(8)
    picture_paragraph.paragraph_format.space_after = Pt(3)
    picture_paragraph.paragraph_format.keep_with_next = True
    picture_paragraph.add_run().add_picture(str(path), width=Cm(width))

    cap = doc.add_paragraph(style="Caption")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_rich(cap, caption, size=10, color=NAVY, italic=True)
    cap.paragraph_format.keep_with_next = False


def add_page_section(doc, landscape=False):
    """Start a new page section, portrait or landscape, with matching margins."""
    new_section = doc.add_section(WD_SECTION.NEW_PAGE)
    if landscape:
        new_section.orientation = WD_ORIENT.LANDSCAPE
        new_section.page_width = Cm(29.7)
        new_section.page_height = Cm(21.0)
        new_section.top_margin = Cm(2.0)
        new_section.bottom_margin = Cm(2.0)
        new_section.left_margin = Cm(2.0)
        new_section.right_margin = Cm(2.0)
    else:
        new_section.orientation = WD_ORIENT.PORTRAIT
        new_section.page_width = Cm(21.0)
        new_section.page_height = Cm(29.7)
        new_section.top_margin = Cm(2.4)
        new_section.bottom_margin = Cm(2.2)
        new_section.left_margin = Cm(2.6)
        new_section.right_margin = Cm(2.4)
    new_section.header_distance = Cm(1.2)
    new_section.footer_distance = Cm(1.1)
    clear_page_number_restart(new_section)
    return new_section


def add_body(doc, text, space_after=7, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12):
    paragraph = doc.add_paragraph(style="Normal")
    paragraph.alignment = align
    add_rich(paragraph, text, size=size)
    paragraph.paragraph_format.space_after = Pt(space_after)
    return paragraph


def add_bullet(doc, text, number=None):
    paragraph = doc.add_paragraph(style="Bullet")
    if number is None:
        marker = "•  "
    else:
        marker = f"{number}.  "
    run = paragraph.add_run(marker)
    style_run(run, size=12, bold=number is not None, color=NAVY)
    add_rich(paragraph, text, size=12)
    return paragraph


def add_front_heading(doc, text, size=15):
    paragraph = doc.add_paragraph(style="FrontHeading")
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_rich(paragraph, text, size=size, color=INK, bold=True)
    return paragraph


def add_heading(doc, text, level=1, page_break=True):
    paragraph = doc.add_paragraph(style=f"Heading {level}")
    paragraph.paragraph_format.page_break_before = page_break
    add_rich(paragraph, text, size={1: 16, 2: 13.5, 3: 12.5}[level], color=INK, bold=True)
    return paragraph


def add_toc_field(doc):
    paragraph = doc.add_paragraph(style="TOC 1")
    paragraph.paragraph_format.space_before = Pt(6)
    paragraph.paragraph_format.space_after = Pt(4)

    begin_run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    begin_run._r.append(begin)

    instr_run = paragraph.add_run()
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = ' TOC \\o "1-3" \\h \\z \\u '
    instr_run._r.append(instr)

    separate_run = paragraph.add_run()
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    separate_run._r.append(separate)

    text_run = paragraph.add_run()
    text = OxmlElement("w:t")
    text.text = "Table of contents will update when this document is opened in Microsoft Word."
    text_run._r.append(text)

    end_run = paragraph.add_run()
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    end_run._r.append(end)


def add_toc_line(doc, label, page):
    paragraph = doc.add_paragraph(style="TOC 1")
    paragraph.paragraph_format.space_after = Pt(5)
    add_rich(paragraph, label, size=11.5, color=INK)
    run = paragraph.add_run("\t" + page)
    style_run(run, size=11.5, color=INK)


# ---------------------------------------------------------------------------
# Document setup
# ---------------------------------------------------------------------------


doc = Document()
section = doc.sections[0]
section.page_width = Cm(21.0)
section.page_height = Cm(29.7)
section.top_margin = Cm(2.4)
section.bottom_margin = Cm(2.2)
section.left_margin = Cm(2.6)
section.right_margin = Cm(2.4)
section.header_distance = Cm(1.2)
section.footer_distance = Cm(1.1)

styles = doc.styles
normal = styles["Normal"]
force_font(normal)
normal.font.size = Pt(12)
normal.font.color.rgb = INK
normal.paragraph_format.line_spacing = 1.5
normal.paragraph_format.space_after = Pt(7)
normal.paragraph_format.widow_control = True

for level, size, before, after in ((1, 16, 0, 16), (2, 13.5, 14, 8), (3, 12.5, 12, 6)):
    style = styles[f"Heading {level}"]
    force_font(style)
    style.font.size = Pt(size)
    style.font.bold = True
    style.font.color.rgb = INK
    style.paragraph_format.space_before = Pt(before)
    style.paragraph_format.space_after = Pt(after)
    style.paragraph_format.keep_with_next = True
    style.paragraph_format.line_spacing = 1.15
    if level == 1:
        style.paragraph_format.page_break_before = True

caption = styles["Caption"]
force_font(caption)
caption.font.size = Pt(10)
caption.font.italic = True
caption.font.color.rgb = NAVY
caption.paragraph_format.space_before = Pt(0)
caption.paragraph_format.space_after = Pt(12)
caption.paragraph_format.line_spacing = 1.0

front_heading = styles.add_style("FrontHeading", WD_STYLE_TYPE.PARAGRAPH)
front_heading.base_style = normal
force_font(front_heading)
front_heading.font.size = Pt(15)
front_heading.font.bold = True
front_heading.paragraph_format.space_before = Pt(0)
front_heading.paragraph_format.space_after = Pt(18)
front_heading.paragraph_format.keep_with_next = True
front_heading.paragraph_format.line_spacing = 1.0

table_caption = styles.add_style("TableCaption", WD_STYLE_TYPE.PARAGRAPH)
table_caption.base_style = normal
force_font(table_caption)
table_caption.font.size = Pt(9.5)
table_caption.font.bold = True
table_caption.paragraph_format.space_before = Pt(10)
table_caption.paragraph_format.space_after = Pt(4)
table_caption.paragraph_format.line_spacing = 1.0
table_caption.paragraph_format.keep_with_next = True

bullet = styles.add_style("Bullet", WD_STYLE_TYPE.PARAGRAPH)
bullet.base_style = normal
force_font(bullet)
bullet.paragraph_format.left_indent = Cm(0.9)
bullet.paragraph_format.first_line_indent = Cm(-0.55)
bullet.paragraph_format.space_after = Pt(6)
bullet.paragraph_format.line_spacing = 1.35
bullet.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

for name, size, indent in (("TOC 1", 11.5, 0.0), ("TOC 2", 11.0, 0.65), ("TOC 3", 10.5, 1.25)):
    try:
        toc_style = styles[name]
    except KeyError:
        toc_style = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    toc_style.base_style = normal
    force_font(toc_style)
    toc_style.font.size = Pt(size)
    toc_style.paragraph_format.left_indent = Cm(indent)
    toc_style.paragraph_format.space_after = Pt(4)
    toc_style.paragraph_format.line_spacing = 1.0
    tabs = toc_style.paragraph_format.tab_stops
    tabs.add_tab_stop(Cm(15.8), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)

doc.core_properties.title = "Candidate Lab - Project Stage-1 Report"
doc.core_properties.author = ", ".join(name for name, _ in STUDENTS)
doc.core_properties.subject = TITLE
doc.core_properties.keywords = "candidate matching; explainable AI; fairness; information retrieval; human review"
doc.core_properties.comments = "Project Stage-1 report, Department of CSE (AI&ML), VJIT."

# Cover page has no page number. The next section uses roman numerals.
section.footer.is_linked_to_previous = False
section.footer.paragraphs[0].text = ""

# ---------------------------------------------------------------------------
# Cover page
# ---------------------------------------------------------------------------


def cover_line(text, size, color=INK, bold=False, italic=False, before=0, after=0, caps=False):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(before)
    paragraph.paragraph_format.space_after = Pt(after)
    paragraph.paragraph_format.line_spacing = 1.0
    add_rich(paragraph, text.upper() if caps else text, size=size, color=color, bold=bold, italic=italic)
    return paragraph


banner_paragraph = doc.add_paragraph()
banner_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
banner_paragraph.paragraph_format.space_before = Pt(0)
banner_paragraph.paragraph_format.space_after = Pt(8)
banner_paragraph.add_run().add_picture(str(ASSETS / "image2.jpeg"), width=Cm(15.7))

cover_line("A Project Stage-1 Report", 12.5, NAVY, bold=True, italic=True, after=2)
cover_line("On", 11.5, NAVY, bold=True, italic=True, after=8)
cover_line(TITLE, 16.5, RED, bold=True, after=12)
cover_line(
    "Submitted In partial fulfilment for the award of the Degree of",
    11.5,
    NAVY,
    bold=True,
    italic=True,
    after=8,
)
cover_line("BACHELOR OF TECHNOLOGY", 14, RED, bold=True, after=5)
cover_line("In", 11, INK, italic=True, after=5)
cover_line("COMPUTER SCIENCE & ENGINEERING", 14, RED, bold=True, after=4)
cover_line("(Artificial Intelligence & Machine Learning)", 12.5, RED, bold=True, after=10)
cover_line("by", 11, INK, italic=True, after=5)
for name, roll in STUDENTS:
    cover_line(f"{name}  ({roll})", 11.8, RED, bold=True, italic=True, after=2)
cover_line("Under the guidance of", 10.5, NAVY, bold=True, italic=True, before=12, after=4)
cover_line(GUIDE, 11.8, RED, bold=True, after=2)
cover_line(GUIDE_DESIGNATION, 11, RED, after=8)

logo_paragraph = doc.add_paragraph()
logo_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
logo_paragraph.paragraph_format.space_before = Pt(0)
logo_paragraph.paragraph_format.space_after = Pt(10)
logo_paragraph.add_run().add_picture(str(ASSETS / "image1.jpeg"), width=Cm(2.1))

cover_line("DEPARTMENT OF " + DEPARTMENT, 10.5, INK, bold=True, after=5)
cover_line(COLLEGE, 15, RED, bold=True, after=2)
cover_line("(An Autonomous Institution)", 10.5, RED, after=3)
cover_line(
    "Approved by AICTE, Accredited by NAAC, NBA & permanently Affiliated to JNTUH",
    8.8,
    NAVY,
    bold=True,
    after=6,
)
cover_line(YEAR, 10.5, INK, bold=True, after=0)

# ---------------------------------------------------------------------------
# Front matter
# ---------------------------------------------------------------------------

front_section = doc.add_section(WD_SECTION.NEW_PAGE)
front_section.footer.is_linked_to_previous = False
front_section.footer.paragraphs[0].text = ""
front_section.footer.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
add_page_field(front_section.footer.paragraphs[0])
set_page_number_format(front_section, "lowerRoman", 2)

# Certificate -----------------------------------------------------------------
cert_banner = doc.add_paragraph()
cert_banner.alignment = WD_ALIGN_PARAGRAPH.CENTER
cert_banner.paragraph_format.space_before = Pt(0)
cert_banner.paragraph_format.space_after = Pt(30)
cert_banner.add_run().add_picture(str(ASSETS / "image2.jpeg"), width=Cm(13.5))

add_front_heading(doc, "CERTIFICATE", size=14)
certificate = (
    "This is to certify that the Project Stage-1 report entitled **" + TITLE + "** "
    "submitted by **Deekshith Alle (23911A6672), Sirivennala Kammari (23911A6698), "
    "Rizwana Mohammad (23911A66A9), and Harshavardhan Dyavanapelli (24915A6608)** "
    "to Vidya Jyothi Institute of Technology, Hyderabad, in partial fulfillment for the award "
    "of the degree of **B.Tech CSE (AI&ML)** is a bonafide record of project work carried out "
    "by them under my supervision. The contents of this report, in full or in parts, have not "
    "been submitted to any other Institution or University for the award of any degree."
)
certificate_paragraph = add_body(doc, certificate, space_after=0, align=WD_ALIGN_PARAGRAPH.LEFT)
certificate_paragraph.paragraph_format.line_spacing = 1.5
certificate_paragraph.paragraph_format.space_before = Pt(4)

for _ in range(9):
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(0)
    spacer.paragraph_format.line_spacing = 1.0

signature_table = doc.add_table(rows=1, cols=2)
signature_table.alignment = WD_TABLE_ALIGNMENT.CENTER
signature_table.autofit = False
signature_table.allow_autofit = False
remove_table_borders(signature_table)
left, right = signature_table.rows[0].cells
for cell, lines in (
    (left, ("Signature of Supervisor", GUIDE, GUIDE_DESIGNATION, "Department of CSE (AI&ML)")),
    (right, ("Signature of HOD", HOD, HOD_DESIGNATION, "Department of CSE (AI&ML)")),
):
    cell.width = Cm(7.4)
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(3)
    paragraph.paragraph_format.line_spacing = 1.15
    first = paragraph.add_run(lines[0])
    style_run(first, size=11.5, bold=True, color=INK)
    for line in lines[1:]:
        p = cell.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(line)
        style_run(run, size=11.5, bold=(line == lines[1]), color=INK)

doc.add_page_break()

# Acknowledgement -------------------------------------------------------------
add_front_heading(doc, "ACKNOWLEDGEMENT", size=14)
ack_paragraphs = [
    "Any endeavor in the field of development is a person's intensive activity. A successful "
    "project is a fruitful culmination of efforts by many people, some directly involved and "
    "some others who have quietly encouraged and supported.",
    "We express our profound gratitude to **" + GUIDE + "**, **" + GUIDE_DESIGNATION + "** of "
    "CSE (AI&ML), for her continuous encouragement, patient guidance and valuable suggestions "
    "that helped us ensure successful results in all our endeavors.",
    "We would like to thank **" + HOD + "**, **Head of the Department**, Department of CSE "
    "(AI&ML), who has patiently guided and helped us throughout this project and our academic "
    "work.",
    "We wish to express our heartfelt thanks to the Principal, **" + PRINCIPAL + "**, whose "
    "support and encouragement were indispensable to us during the course.",
    "We wish to express our heartfelt thanks to our **College Management**, for providing the "
    "infrastructure, laboratory facilities and academic environment required during the course.",
    "We are also grateful to the faculty members and technical staff of the Department of CSE "
    "(AI&ML) for their assistance during reviews, demonstrations and verification activities.",
    "Last but not least, we thank our family members and friends who are the backbone of our "
    "efforts and who provide support in every possible way.",
]
for text in ack_paragraphs:
    add_body(doc, text, space_after=12)

for _ in range(4):
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(0)
    spacer.paragraph_format.line_spacing = 1.0

by_paragraph = doc.add_paragraph()
by_paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
by_paragraph.paragraph_format.space_after = Pt(10)
by_run = by_paragraph.add_run("By")
style_run(by_run, size=12, color=INK)

for name, roll in STUDENTS:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(f"{name}  ({roll})")
    style_run(run, size=12, color=INK)

doc.add_page_break()

# Abstract --------------------------------------------------------------------
add_front_heading(doc, "ABSTRACT", size=14)
abstract_paragraphs = [
    "Candidate screening requires a reviewer to connect the skills described in a resume with "
    "the skills required by a job. Resumes differ in structure, vocabulary and level of detail; "
    "job descriptions mix essential requirements with desirable qualifications; and a score "
    "without visible evidence is difficult to interpret, reproduce or challenge. Candidate Lab "
    "is a local, role-aware decision-support application that addresses this inspectability "
    "problem. It combines document extraction, explicit required and preferred skill rubrics, "
    "evidence-linked matching, immutable profile and run snapshots, candidate applications, "
    "recruiter decisions and a restricted aggregate audit view.",
    "The implemented baseline is deliberately transparent. Candidate profiles are parsed from "
    "text PDF, DOCX or TXT files, or pasted text, and are previewed and corrected before saving. "
    "A context-aware dictionary identifies supported, learning, uncertain and negated skill "
    "mentions and retains the supporting passage. Matching combines required-skill coverage "
    "(60%), preferred-skill coverage (15%) and lexical alignment (25%), or 75% required coverage "
    "when no preferred skills exist. Every score component is shown as an exact arithmetic "
    "contribution. A local Sentence Transformers model can replace the lexical alignment term "
    "when explicitly configured; the default method is skill-tfidf-v2 with context-rules-v2.",
    "The prototype separates the candidate, recruiter and auditor roles at the server boundary. "
    "Candidates manage owned profiles and applications; recruiters publish jobs, inspect "
    "evidence and record reasoned decisions; auditors see aggregate cohort rates, Wilson "
    "intervals and event records without receiving individual resume text or ranking snapshots. "
    "Synthetic Cohort A/B labels are used only for demonstration and never enter the ranking "
    "path. Verification currently covers 26 backend/API tests and 9 production-build browser "
    "journeys, together with type checking, linting and a production build.",
    "The project does not claim a trained hiring predictor, measured hiring accuracy or "
    "real-world fairness. Its contribution is an inspectable baseline, a traceable workflow and "
    "an honest evaluation frame that distinguishes demonstrated functionality from claims that "
    "require a representative, consented and labelled dataset.",
]
for text in abstract_paragraphs:
    p = add_body(doc, text, space_after=10)
    p.paragraph_format.line_spacing = 1.3

doc.add_page_break()

# Contents --------------------------------------------------------------------
add_front_heading(doc, "TABLE OF CONTENTS", size=14)
add_toc_line(doc, "ABSTRACT", "iv")
add_toc_field(doc)

# ---------------------------------------------------------------------------
# Body
# ---------------------------------------------------------------------------

body_section = doc.add_section(WD_SECTION.NEW_PAGE)
body_section.footer.is_linked_to_previous = False
body_section.footer.paragraphs[0].text = ""
body_section.footer.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
add_page_field(body_section.footer.paragraphs[0])
set_page_number_format(body_section, "decimal", 1)

# Chapter 1 -------------------------------------------------------------------
chapter1 = add_heading(doc, "CHAPTER 1  INTRODUCTION", 1, page_break=False)
add_heading(doc, "1.1 Introduction", 2, page_break=False)
add_body(
    doc,
    "Recruitment is a decision-making process in which a reviewer must judge whether a person's "
    "documented experience is relevant to a job. Resumes are heterogeneous: one candidate lists "
    "technologies in a compact skills section, another describes projects in prose, and a third "
    "combines education, internships and open-source work in a format that no single parser can "
    "anticipate. Job descriptions are equally varied. They combine mandatory technologies with "
    "desirable tools, responsibilities, seniority expectations and organisational context. A "
    "screening system therefore has to do more than count words. It has to preserve the connection "
    "between a requirement, the evidence found in a document and the judgment made by a reviewer.",
)
add_body(
    doc,
    "Conventional applicant tracking systems often reduce this problem to keyword filters or a "
    "single opaque relevance score. Keyword filters are fast and easy to explain, but they miss "
    "aliases, abbreviations and semantically equivalent phrasing. Learned ranking models can "
    "capture more subtle relationships, but they depend on labelled data, can reproduce historical "
    "selection patterns and are difficult to audit when their features and training population are "
    "not documented. A numerical score alone does not tell a candidate why evidence was missed, "
    "does not tell a recruiter which passage supported a decision, and does not tell an auditor "
    "whether the comparison was based on a valid outcome label.",
)
add_body(
    doc,
    "Candidate Lab was developed as a local research application around these concerns. It "
    "provides a browser interface for three roles. Candidates create and correct profiles, browse "
    "published opportunities and apply with a saved profile snapshot. Recruiters define jobs with "
    "explicit required and preferred skills, inspect a ranked set of active applications, examine "
    "the exact contribution of each score component and record a reasoned recruitment decision. "
    "Auditors inspect aggregate cohort comparisons and an append-only activity record. The "
    "application is intentionally small enough to run on a laptop, but its boundaries are enforced "
    "on the server rather than only in the interface.",
)
add_body(
    doc,
    "The project title refers to fair and explainable machine learning, but the implemented "
    "release does not pretend to be a trained predictor of hiring success. Its default matcher is "
    "a transparent heuristic: dictionary evidence, context rules and TF-IDF alignment. This "
    "choice makes every input and every arithmetic term inspectable. It also exposes the limits "
    "of lexical matching: a mention of a technology is not proof of proficiency, a missing phrase "
    "is not proof that a skill is absent, and a high score is not a calibrated probability. Those "
    "limits are part of the design, not an afterthought.",
)
add_body(
    doc,
    "The Stage-1 work reported here covers the problem definition, the relevant literature, the "
    "data and preprocessing pipeline, the architecture and design models, the implemented "
    "prototype and the verification evidence. The report uses the structure supplied by the "
    "department. Chapter 1 introduces the problem and objectives. Chapter 2 reviews existing "
    "approaches and states the proposed system. Chapter 3 explains the methodology, including the "
    "architecture, data flow, class, sequence, state and activity models. Chapter 4 summarises the "
    "implementation and verification. Chapter 5 concludes the work and identifies the next "
    "research steps. References and an honest proof-of-publication placeholder follow the "
    "conclusion.",
)

add_heading(doc, "1.2 Problem Statement", 2, page_break=False)
add_body(
    doc,
    "Manual shortlisting is flexible but difficult to reproduce. Two reviewers may read the same "
    "resume and apply different criteria; a later reviewer may not know which version of the "
    "resume was considered; and a candidate may never learn that a relevant project was ignored "
    "because the document used an unexpected term. These are not only usability problems. They "
    "affect the accountability of a decision that can influence a person's access to employment.",
)
add_body(
    doc,
    "Automated tools can reduce effort, but they introduce a new set of problems. A keyword "
    "filter may reward repeated words rather than relevant ability. A machine-learned ranker may "
    "learn from previous decisions that contain historical bias. A semantic model may appear "
    "fluent while remaining unable to justify a particular ranking. An audit dashboard may report "
    "group differences without the qualification labels needed to distinguish a selection-rate "
    "gap from an error-rate gap. In each case, the presence of a number can create more confidence "
    "than the evidence supports.",
)
add_body(
    doc,
    "The technical problem is to transform heterogeneous candidate documents and explicit job "
    "requirements into a traceable comparison, while preserving the evidence, version and role "
    "context needed to review that comparison. The research problem is to do this without "
    "overstating what the comparison establishes. A credible prototype must make its assumptions "
    "visible, separate the ranking from the human decision, keep audit attributes out of the "
    "scoring path and state clearly which fairness questions cannot be answered with the available "
    "data.",
)
add_body(
    doc,
    "Formally, the project develops a local, role-aware decision-support application that (i) "
    "accepts candidate evidence and job rubrics, (ii) extracts inspectable skill evidence, (iii) "
    "calculates an explicit matching index with visible contributions, (iv) stores immutable "
    "snapshots and reasoned decisions, (v) restricts candidate, recruiter and auditor access, and "
    "(vi) provides an aggregate audit demonstration with documented limitations. The application "
    "is a research and demonstration artefact; it is not an autonomous hiring system.",
)

add_heading(doc, "1.3 Objectives", 2, page_break=False)
add_body(
    doc,
    "The objectives translate the problem statement into verifiable engineering outcomes. Each "
    "objective is associated with a success indicator that can be examined in the implementation "
    "or in the verification record.",
)
objectives = [
    (
        "Evidence preparation. Accept text PDF, DOCX and UTF-8 TXT files or pasted text, extract "
        "readable text, identify skill passages and require the user to preview and correct the "
        "result before persistence.",
        "A supported file produces an editable preview; malformed, encrypted, oversized or "
        "unsupported files return a clear validation error.",
    ),
    (
        "Transparent comparison. Represent a job as explicit required and preferred skills, "
        "calculate coverage and alignment terms, and display the exact point contribution of each "
        "term together with the supporting passage.",
        "The displayed contributions sum to the saved score within rounding; every requirement "
        "shows either a passage or an explicit no-evidence status.",
    ),
    (
        "Traceability. Preserve profile versions, application snapshots, immutable matching runs "
        "and recruitment decision revisions so that a later correction does not rewrite history.",
        "A stale profile update returns a conflict; an old run retains its original profile "
        "version and evidence after the profile is edited.",
    ),
    (
        "Controlled access. Enforce candidate ownership and recruiter/auditor role boundaries on "
        "the server, and require an expiring invitation for privileged registration.",
        "Unauthenticated, cross-owner, cross-role and invalid-invitation requests are rejected "
        "even when the browser route is guessed.",
    ),
    (
        "Auditable comparison. Provide an auditor-only aggregate report over a saved run and a "
        "common cutoff, with sample sizes, Wilson intervals, small-group suppression and JSON "
        "export.",
        "Rates are suppressed below five records; the report identifies its synthetic provenance "
        "and does not expose individual resume text or ranking snapshots.",
    ),
    (
        "Verification. Exercise calculation, API and browser workflows in isolated databases and "
        "document both the demonstrated behaviour and the claims that remain unverified.",
        "The backend and browser suites pass, the production build succeeds, and the report "
        "separates functional verification from model-quality and fairness claims.",
    ),
]
for index, (objective, indicator) in enumerate(objectives, start=1):
    add_bullet(doc, f"**{objective.split('.')[0]}.** {objective.split('.', 1)[1].strip()}", number=f"O{index}")
    indicator_paragraph = doc.add_paragraph(style="Normal")
    indicator_paragraph.paragraph_format.left_indent = Cm(0.9)
    indicator_paragraph.paragraph_format.space_after = Pt(7)
    indicator_paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    add_rich(indicator_paragraph, "**Success indicator:** " + indicator, size=11)

add_table(
    doc,
    "Table 1.1: Objectives mapped to verification evidence",
    ["Objective", "Primary evidence", "Where reported"],
    [
        ["O1 Evidence preparation", "Parser tests for TXT, DOCX, PDF and rejection cases", "Chapter 4, Table 4.3"],
        ["O2 Transparent comparison", "Score arithmetic, contribution and passage checks", "Chapter 3; Chapter 4"],
        ["O3 Traceability", "Version-conflict and immutable-snapshot tests", "Chapter 4, Table 4.3"],
        ["O4 Controlled access", "Role, ownership and invitation tests", "Chapter 4, Table 4.3"],
        ["O5 Auditable comparison", "Suppression and interval tests; synthetic audit fixture", "Chapter 3; Chapter 4"],
        ["O6 Verification", "pytest, Playwright, typecheck, lint and build", "Chapter 4, Table 4.3"],
    ],
    [4.0, 7.8, 3.9],
)

# Chapter 2 -------------------------------------------------------------------
add_heading(doc, "CHAPTER 2  LITERATURE SURVEY", 1)
add_heading(doc, "2.1 Existing System", 2, page_break=False)
add_body(
    doc,
    "Existing candidate-screening practice can be grouped into manual review, keyword or Boolean "
    "search, lexical information retrieval, semantic representation, supervised ranking, "
    "post-hoc explanation and fairness auditing. These approaches are complementary, but each "
    "addresses only part of the inspectability problem.",
)
add_body(
    doc,
    "Manual shortlisting remains common in small organisations. A recruiter reads each resume, "
    "compares it with the job description and records a judgement. This approach can use context "
    "that a simple parser cannot: a project may demonstrate a skill even when the exact tool name "
    "is absent, and a candidate's progression may matter more than a keyword count. The weakness "
    "is consistency. Different reviewers apply different thresholds, reasons are often not "
    "retained in a structured form, and a later correction can make it difficult to reconstruct "
    "the document that was originally reviewed.",
)
add_body(
    doc,
    "Keyword and Boolean filters are the simplest automated alternative. They are fast, "
    "deterministic and easy to configure, and they remain useful for narrowing a large candidate "
    "pool. Their limitation is vocabulary sensitivity: a filter for 'PostgreSQL' may not match "
    "'Postgres', a filter for 'REST APIs' may not match 'RESTful services', and a negated mention "
    "such as 'no experience with Docker' can be counted as a positive hit. Keyword counts also "
    "reward repetition rather than demonstrated use.",
)
add_body(
    doc,
    "Lexical information retrieval provides a more principled baseline. TF-IDF represents a "
    "document as weighted term features, giving more weight to terms that are frequent in the "
    "document but less common across the corpus, and cosine similarity measures the angular "
    "alignment between a query vector and a document vector [1]. The approach is local, "
    "reproducible and inexpensive. It is still a bag-of-words method: paraphrases, synonyms and "
    "long-range context may be missed, and a document can score highly because it repeats the "
    "query vocabulary rather than because it demonstrates competence.",
)
add_body(
    doc,
    "Semantic sentence representations address some of the vocabulary problem. Sentence-BERT "
    "uses a Siamese network to derive sentence embeddings that can be compared with cosine "
    "similarity [2]. Such representations can align 'built a Flask service' with a request for "
    "Python web development even when the words differ. They introduce new dependencies, model "
    "licensing and hardware costs, and they remain statistical representations: similarity is not "
    "evidence of proficiency, and a domain-shifted resume corpus may not be represented well. A "
    "semantic model can also make errors harder to explain because its decision is distributed "
    "across many dimensions.",
)
add_body(
    doc,
    "Supervised ranking and learning-to-rank methods can fit labelled relevance or hiring "
    "outcomes when a suitable dataset exists. They may capture interactions that hand-written "
    "rules miss, but they inherit the label-generation process. Historical hiring decisions can "
    "encode prior disadvantage, and feedback loops can reinforce the candidates who were previously "
    "shown or selected. A model that predicts a historical decision is not necessarily a model "
    "that identifies job-relevant ability. Evaluation therefore requires a documented relevance "
    "rubric, representative sampling and a held-out split.",
)
add_body(
    doc,
    "Explanation methods such as SHAP attribute a learned model's prediction to input features "
    "[5]. They are valuable when the underlying model is opaque, but they explain a model rather "
    "than validate its training data or its use. For a small, explicit scoring rubric, a direct "
    "arithmetic breakdown is often more faithful than a post-hoc approximation. Candidate Lab "
    "therefore shows the exact contribution of required coverage, preferred coverage and text "
    "alignment, and does not describe those contributions as causal explanations or SHAP values.",
)
add_body(
    doc,
    "Fairness research distinguishes several criteria. Demographic parity compares selection "
    "rates across groups; equalized odds compares true-positive and false-positive rates "
    "conditional on the true qualification label [6]. The second family of criteria cannot be "
    "estimated without valid labels, and neither family can be established from arbitrary group "
    "labels or a small synthetic sample. Wilson intervals provide a way to express the uncertainty "
    "of a rate estimated from a finite sample [10], but wide intervals are a warning, not a "
    "fairness certificate. An audit dashboard should state which quantities it can and cannot "
    "estimate.",
)
add_body(
    doc,
    "Document parsing is a separate source of error. PDF text extraction depends on the PDF's "
    "internal structure and fails for scanned images without OCR; DOCX extraction must handle "
    "paragraphs, tables and compressed archives [3,4]. Parser failures can remove relevant "
    "evidence or introduce ordering artefacts. A practical system should show the extracted text "
    "and allow correction before the text is used for matching. It should also bound file size, "
    "page count and archive expansion to avoid resource exhaustion.",
)
add_body(
    doc,
    "The gap addressed by this project is not a new ranking algorithm. It is the integration of "
    "explicit job criteria, inspectable evidence, versioned records, role boundaries, human "
    "decisions and an honest audit demonstration in one small application. Table 2.1 summarises "
    "the approaches and the specific limitation that motivates the design.",
)

add_table(
    doc,
    "Table 2.1: Existing approaches and their limitations",
    ["Approach", "Representative methods", "Strength", "Limitation for this project"],
    [
        ["Manual shortlisting", "Reviewer reads each resume", "Contextual judgement", "Inconsistent criteria; limited structured traceability"],
        ["Keyword / Boolean ATS", "Exact terms and filters", "Fast; simple to operate", "Misses aliases and context; negation errors"],
        ["Lexical retrieval", "TF-IDF and cosine similarity [1]", "Local; reproducible baseline", "Wording-sensitive; similarity is not competence"],
        ["Semantic retrieval", "Sentence-BERT embeddings [2]", "Handles paraphrase", "Model cost; still statistical; harder to inspect"],
        ["Supervised ranking", "Learning-to-rank; outcome models", "Can fit labelled data", "Labels scarce or biased; feedback loops; opacity"],
        ["Post-hoc explanation", "SHAP / LIME [5]", "Explains learned predictions", "Approximation; does not validate evidence or data"],
        ["Fairness audit", "Group rates; equalized odds [6]", "Makes disparities visible", "Needs labels and attributes; small-sample uncertainty"],
    ],
    [3.3, 4.5, 3.4, 4.5],
    font_size=8.8,
)

add_heading(doc, "2.2 Proposed System", 2, page_break=False)
add_body(
    doc,
    "Candidate Lab proposes an evidence-led decision-support system rather than an autonomous "
    "ranker. The unit of comparison is a saved application snapshot: a job rubric, a confirmed "
    "profile version and the evidence extracted from that version. The recruiter sees a matching "
    "index and the passages that produced it. The index is an ordering aid; the decision remains a "
    "separate, attributed human action. This separation is the central design choice.",
)
add_body(
    doc,
    "The system is organised around six principles. First, the job rubric is explicit: required "
    "and preferred skills are stored separately and validated. Second, evidence precedes score: "
    "each requirement is linked to a supporting sentence or an explicit not-found status. Third, "
    "history is preserved: profile versions, application revisions, run snapshots and decision "
    "revisions are append-only records. Fourth, access is enforced at the server: a browser cannot "
    "grant itself a role by changing a visible control. Fifth, audit attributes are separated from "
    "the ranking path: synthetic Cohort A/B labels are stored in a different table and are never "
    "passed to the matcher. Sixth, claims are bounded: the interface and documentation state what "
    "the system does not establish.",
)
add_body(
    doc,
    "The end-to-end workflow is: a candidate saves a confirmed profile and applies to a published "
    "job; the application stores a snapshot of that profile; a recruiter opens the applicants for "
    "the job and starts a matching run; the run ranks only active submitted snapshots and stores "
    "the rubric, method, evidence and score contributions; the recruiter inspects evidence and "
    "records a decision with a revision; an auditor selects a saved run, changes a common cutoff "
    "and examines aggregate rates and activity events. Each transition has a server-side check and "
    "an audit event where appropriate.",
)
add_body(
    doc,
    "Compared with the existing approaches in Table 2.1, the proposed system does not attempt to "
    "outperform a trained ranker. It attempts to make a bounded comparison inspectable and "
    "reproducible. Table 2.2 maps the identified gaps to specific design responses.",
)

add_table(
    doc,
    "Table 2.2: Gap-to-design mapping",
    ["Identified gap", "Candidate Lab response", "Evidence in this report"],
    [
        ["Opaque score", "Three visible weighted contributions and exact arithmetic", "Section 3.3.1; Figure 3.5"],
        ["Inconsistent criteria", "Per-job required and preferred skill rubric", "Section 3.1; Section 4.3"],
        ["Lost correction history", "Profile versions and immutable run snapshots", "Section 3.1; Figure 3.4"],
        ["Role leakage", "Server-enforced role and ownership dependencies", "Section 3.2; Section 4.4"],
        ["Unqualified fairness claim", "Synthetic provenance, suppression, intervals and limitations", "Section 3.3.1; Figure 3.6"],
        ["Parser errors", "Editable preview and explicit validation errors", "Section 3.1; Chapter 4"],
        ["No evaluation frame", "Synthetic benchmark with NDCG, recall and precision", "Section 4.3; Chapter 4"],
    ],
    [4.0, 7.7, 4.0],
)

add_body(
    doc,
    "The scope is intentionally local and bounded. The prototype does not include OCR, a "
    "production identity provider, multi-organisation tenancy, background workers, email delivery "
    "or a representative labelled dataset. Optional PostgreSQL and container configuration are "
    "supplied, but the verified deployment is a single Windows laptop serving a loopback address. "
    "These boundaries are stated so that a successful demonstration is not mistaken for evidence "
    "of production readiness or real-world fairness.",
)

# Chapter 3 -------------------------------------------------------------------
add_heading(doc, "CHAPTER 3  METHODOLOGY", 1)
add_heading(doc, "3.1 Data Collection and Preprocessing", 2, page_break=False)
add_body(
    doc,
    "The methodology uses four kinds of data: candidate documents, job descriptions, a synthetic "
    "demonstration workspace and a synthetic relevance fixture for evaluation. These sources serve "
    "different purposes. Candidate and job data support the operational workflow; the demo seed "
    "makes the workflow reproducible; the evaluation fixture exercises ranking metrics without "
    "pretending to be a representative applicant sample.",
)

add_table(
    doc,
    "Table 3.1: Data sources and their role",
    ["Source", "Contents", "Use", "Important limitation"],
    [
        ["Candidate document", "Text PDF, DOCX or UTF-8 TXT; or pasted text up to 30,000 characters", "Profile evidence and skill extraction", "No OCR; parser may miss layout or scanned text"],
        ["Job description", "Recruiter-authored title, description and explicit skill lists", "Rubric and alignment query", "Quality depends on the recruiter's rubric"],
        ["Demo workspace", "12 fictional profiles, 3 jobs, 1 application, 2 saved runs", "Reproducible walkthrough and UI inspection", "Small, synthetic and not representative"],
        ["Evaluation fixture", "2 queries, 4 fictional profiles per query, relevance grades 0/1/2", "Metric smoke test for the evaluation page", "Hand-authored; not independently annotated"],
        ["Audit attributes", "Synthetic Cohort A/B labels for the demo profiles", "Aggregate report demonstration", "Not demographic identity; never a ranking input"],
    ],
    [3.0, 5.3, 4.0, 3.4],
    font_size=8.8,
)

add_body(
    doc,
    "Candidate input is accepted through a multipart upload or a pasted-text form. The upload "
    "endpoint accepts only .pdf, .docx and .txt files, reads at most 2 MB and rejects a request "
    "body larger than 3 MB at the middleware boundary. PDF input must be unencrypted and at most "
    "50 pages; DOCX input is inspected as a ZIP archive before paragraphs and table cells are "
    "read; TXT input is decoded as UTF-8. A malformed, encrypted or unsupported document returns a "
    "422 or 415 response with a recovery instruction. Original uploads are processed in memory and "
    "are not retained.",
)
add_body(
    doc,
    "Extraction produces a draft, not a saved candidate. The interface displays the extracted "
    "text, warning messages and recognised skill evidence. The user can correct the text before "
    "saving. This preview step is important because a parser can reorder columns, drop table "
    "content or merge unrelated lines. Persisting the confirmed text rather than the original file "
    "also reduces the amount of sensitive material stored by the demonstration.",
)
add_body(
    doc,
    "Normalisation converts whitespace, splits text into sentences and clauses, and compares "
    "case-insensitive skill aliases with word-boundary checks. The vocabulary contains 24 "
    "canonical skills, including Python, SQL, PostgreSQL, FastAPI, Django, REST APIs, Docker, Git, "
    "Testing, JavaScript, TypeScript, React, Node.js, HTML, CSS, Machine Learning, Pandas, NumPy, "
    "Data Visualization, Statistics, Excel, AWS, Java, Spring Boot and Communication. Each "
    "canonical skill maps to one or more aliases; for example, SQL also recognises PostgreSQL, "
    "MySQL and SQLite, and Testing recognises pytest, unit tests and integration tests.",
)
add_body(
    doc,
    "A plain dictionary match would treat every mention as positive. The implemented "
    "context-rules-v2 classifier instead labels each observation as supported, learning, "
    "uncertain or negated. It examines the clause before and after a match for negation cues "
    "('no experience with', 'without'), learning cues ('currently learning', 'beginner') and "
    "support cues ('built', 'implemented', 'tested', 'deployed'). If a clause contains both "
    "positive and negative mentions, the result is marked uncertain and a human-verification note "
    "is attached. The first best passage is retained as evidence for the requirement. A skill that "
    "is only mentioned as learning or negation does not earn coverage points.",
)
add_body(
    doc,
    "The matcher does not receive the whole document. A safe scoring text is constructed from "
    "recognised skill-bearing clauses only. Lines containing an email address or an explicit "
    "identity/contact header (for example, name, address, date of birth, gender, religion or "
    "marital status) are removed, and long digit strings are stripped. This is a heuristic "
    "reduction of irrelevant and sensitive text, not complete anonymisation. Identity or proxy "
    "information can remain inside prose, and a reviewer must inspect the actual passage rather "
    "than treating a keyword as proof of ability.",
)
add_body(
    doc,
    "Every saved profile produces a ProfileVersion row. An edit supplies the version that the "
    "user loaded; the server compares it with the current version and performs a conditional "
    "update. A stale edit receives a 409 conflict instead of silently overwriting a newer profile. "
    "When a candidate applies to a published job, the application stores its own snapshot and "
    "revision. A matching run stores the job snapshot, the method identifier, the profile versions "
    "and the full result rows. Later corrections therefore affect future work but do not rewrite "
    "the evidence of an earlier run.",
)
add_body(
    doc,
    "Audit attributes are collected separately. The demo workspace attaches arbitrary Cohort A/B "
    "labels to synthetic profiles; these labels are stored in an audit table and are never passed "
    "to the matcher. Real demographic auditing would require a consent and governance process that "
    "is outside this prototype. The separation is a design safeguard, not a claim that free-text "
    "proxies have been removed.",
)

add_table(
    doc,
    "Table 3.2: Preprocessing stages and outputs",
    ["Stage", "Operation", "Output"],
    [
        ["1. Ingest", "Check extension, size, PDF signature/page count, DOCX archive and UTF-8 decoding", "Accepted bytes or a specific validation error"],
        ["2. Extract", "Read PDF pages, DOCX paragraphs/tables or TXT text", "Raw text and extraction warnings"],
        ["3. Normalise", "Collapse whitespace; split sentences and contrast clauses; normalise case", "Candidate clauses for matching"],
        ["4. Classify evidence", "Apply aliases and context rules", "Supported / learning / uncertain / negated / not_found with a passage"],
        ["5. Build scoring text", "Remove contact/identity headers; keep skill-bearing clauses", "Reduced text for alignment and evidence"],
        ["6. Version", "Create a profile, application or run snapshot", "Immutable record with version and timestamp"],
        ["7. Align", "Fit TF-IDF or compute local embeddings for the run", "Similarity term used in the score"],
    ],
    [3.2, 8.4, 4.1],
    font_size=8.8,
)

add_heading(doc, "3.2 Architecture Diagram", 2, page_break=False)
add_body(
    doc,
    "Candidate Lab uses a layered architecture. The presentation layer is a React and TypeScript "
    "single-page application served by the backend in the production build. The application and "
    "API layer is a FastAPI process that owns session validation, role dependencies, request "
    "validation, origin checks, size limits and static asset delivery. Domain services implement "
    "authentication, profile parsing and extraction, job and publication management, applications "
    "and decisions, matching and audit arithmetic. The data and model layer contains SQLAlchemy "
    "models over SQLite by default (PostgreSQL is an optional configuration) and an optional local "
    "Sentence Transformers model. Figure 3.1 shows the layers and the main interfaces.",
)
add_figure(doc, "architecture.png", "Figure 3.1: Layered architecture of Candidate Lab")

add_body(
    doc,
    "A browser request is sent as JSON or multipart data to the FastAPI boundary. The boundary "
    "resolves the opaque session cookie, loads the user and checks the required role before a "
    "protected service is called. Pydantic models validate field lengths, roles, skill lists, "
    "decision revisions and review reasons. Domain services then use SQLAlchemy sessions to read "
    "or write records. The browser never receives a database credential and cannot grant itself a "
    "role by editing local state.",
)
add_body(
    doc,
    "Two separations are especially important. First, the ranking path receives only the job "
    "rubric and the submitted candidate snapshot; it does not receive audit attributes. Second, "
    "the audit endpoint combines a saved run with aggregate attributes only after an auditor role "
    "check. The same database stores both kinds of data, but the application-level interfaces keep "
    "them apart. This is not a formal information-flow proof, but it makes the intended boundary "
    "visible in the code and in the data-flow model.",
)
add_body(
    doc,
    "The verified deployment is a single Windows laptop. Uvicorn serves the FastAPI application "
    "and the built frontend on 127.0.0.1:8000, and SQLite persists records in a local file. The "
    "Dockerfile and compose configuration describe an optional container/PostgreSQL path, but "
    "they are configuration support rather than a verified public deployment. HTTPS, secure "
    "cookies, backups, identity administration and retention operations would be required before "
    "any shared deployment.",
)

add_table(
    doc,
    "Table 3.3: Architecture layers and responsibilities",
    ["Layer", "Main technology", "Responsibility", "Trust boundary"],
    [
        ["Presentation", "React 19, TypeScript, Vite", "Role-specific screens, forms, evidence ledger, audit controls", "Untrusted browser"],
        ["Application / API", "FastAPI, Pydantic", "Session, role, validation, origin and size checks, static assets", "Server-authoritative"],
        ["Domain services", "Python modules", "Authentication, profiles, jobs, applications, matching, audit", "Server-side"],
        ["Persistence", "SQLAlchemy, SQLite / PostgreSQL", "Users, profiles, versions, jobs, runs, decisions, events", "Database file or service"],
        ["Model", "scikit-learn TF-IDF; optional local MiniLM", "Lexical or semantic alignment term", "Local, offline by default"],
    ],
    [3.1, 4.1, 5.4, 3.3],
    font_size=8.8,
)

add_heading(doc, "3.3 Proposed Methodology", 2, page_break=False)
add_body(
    doc,
    "The proposed methodology combines deterministic evidence extraction, an explicit weighted "
    "score, human review and a separate aggregate audit. It is designed to answer a practical "
    "question: given a job rubric and a submitted profile, which requirements have supporting "
    "evidence, how much does each component contribute, and what record remains after a reviewer "
    "makes a decision? The method is intentionally simpler than a trained ranking system so that "
    "each answer can be inspected.",
)

add_heading(doc, "3.3.1 Matching and Scoring Method", 3, page_break=False)
add_body(
    doc,
    "For each active application, the matcher evaluates every required and preferred skill "
    "against the submitted profile snapshot. Required coverage R is the fraction of required "
    "skills with supported evidence. Preferred coverage P is the fraction of preferred skills "
    "with supported evidence, or zero when the job has no preferred skills. Lexical alignment L is "
    "the cosine similarity between a query formed from the required and preferred skill names and "
    "the profile's skill-bearing text. The matching index is:",
)
formula = doc.add_paragraph()
formula.alignment = WD_ALIGN_PARAGRAPH.CENTER
formula.paragraph_format.space_before = Pt(4)
formula.paragraph_format.space_after = Pt(8)
formula_run = formula.add_run("Score = 100 × (0.60R + 0.15P + 0.25L)")
style_run(formula_run, size=13, bold=True, color=NAVY)

add_table(
    doc,
    "Table 3.4: Score components and weights",
    ["Component", "Definition", "Default weight", "No-preferred-skills case"],
    [
        ["Required skill evidence (R)", "Supported required skills / all required skills", "0.60", "0.75"],
        ["Preferred skill evidence (P)", "Supported preferred skills / all preferred skills", "0.15", "0.00"],
        ["Lexical or semantic alignment (L)", "Cosine similarity between the skill query and the profile text", "0.25", "0.25"],
    ],
    [4.1, 7.4, 2.4, 2.8],
    font_size=9.0,
)

add_body(
    doc,
    "The weights always sum to one. If a job has no preferred skills, the required weight rises "
    "to 0.75 and the preferred weight becomes zero, so the maximum score remains 100. Each "
    "component is multiplied by 100 and rounded to four decimal places; the score is the rounded "
    "sum of those contributions. For example, a profile with R = 1.0, P = 1.0 and L = 0.10 "
    "receives 60 + 15 + 2.5 = 77.5. The interface shows these three terms separately, so a "
    "reviewer can see whether a high score came from explicit coverage or from textual overlap.",
)
add_body(
    doc,
    "The default alignment method is skill-tfidf-v2. A TF-IDF vectoriser is fitted to the query "
    "and the skill-bearing documents for the run, using unigrams and bigrams with sublinear term "
    "frequency. Cosine similarity produces a value between zero and one. Because the vectoriser "
    "is fitted per run, adding or removing profiles can change the alignment term; saved runs "
    "therefore retain their method, cohort and result rows. The alternative skill-semantic-v2 path "
    "uses a locally cached Sentence Transformers model, encodes the query and documents with "
    "normalised embeddings, and clips the dot product to the range zero to one. If the configured "
    "model cannot be loaded, the request fails explicitly rather than silently falling back to a "
    "different method.",
)
add_body(
    doc,
    "Evidence status is not a binary match. A requirement is marked supported only when the "
    "context rules find a positive use of an alias. A learning mention, a negated mention or an "
    "ambiguous mention is reported with its status and does not earn coverage. A not-found result "
    "means only that the supported vocabulary and context rules did not find a passage in the "
    "submitted text. It is not proof that the candidate lacks the skill. Warnings are attached to "
    "the result and displayed with the evidence so that a reviewer can decide whether to request "
    "clarification.",
)
add_body(
    doc,
    "Results are sorted by descending score, with the candidate identifier used as a stable "
    "tie-breaker so that ordering does not depend on audit attributes. The saved run contains the "
    "job snapshot, method identifier, profile version, requirements, evidence passages, component "
    "values, contributions, warnings and the reduced profile snapshot. A later profile correction "
    "creates a new version; the old run remains unchanged. The same principle applies to "
    "applications and recruitment decisions: a new revision is appended, and the previous revision "
    "remains available for reconstruction.",
)
add_body(
    doc,
    "The aggregate audit uses a selected run and a common cutoff t. For each synthetic group g, "
    "the selection rate is the number of profiles with a saved score at least t divided by the "
    "number of audited profiles in that group. The report displays the group sizes, selected "
    "counts and 95% Wilson intervals. A group with fewer than five records has its selected count, "
    "rate and interval suppressed; the sample size remains visible. The displayed difference is "
    "the maximum group rate minus the minimum group rate when at least two groups are comparable. "
    "This is a descriptive research demonstration, not a hiring policy. Without validated "
    "qualification labels, true-positive rates, false-positive rates and equalized odds cannot be "
    "estimated. Without consented demographic attributes and a representative population, the "
    "synthetic A/B report cannot establish real-world fairness.",
)

add_heading(doc, "3.3.2 System Models and Data Flow", 3, page_break=False)
add_body(
    doc,
    "The design is documented with six complementary models. The data-flow diagrams show how "
    "information moves between external entities, processes and data stores. The class diagram "
    "shows the persistent records and their application-level relationships. The sequence diagram "
    "shows the time ordering of an application and a matching request. The state chart shows the "
    "lifecycle of an application. The activity diagram shows the end-to-end workflow, including "
    "the evidence-correction loop and the audit branch.",
)
add_body(
    doc,
    "Figure 3.2 is the Level-0 context diagram. It treats Candidate Lab as a single process with "
    "three external entities: the candidate, the recruiter and the auditor. The candidate supplies "
    "profile evidence and applications and receives application status. The recruiter supplies job "
    "rubrics, publication and review requests and receives ranked evidence and review history. The "
    "auditor supplies a cutoff and report request and receives an aggregate cohort report and audit "
    "events. The diagram deliberately omits internal storage and processing detail so that the "
    "system boundary is clear.",
)
add_figure(doc, "dfd_level0.png", "Figure 3.2: Level-0 data-flow diagram (context)")

add_body(
    doc,
    "Figure 3.3 expands the context into six processes and six data stores. Process 1 manages "
    "accounts and profile evidence; process 2 manages jobs and publication state; process 3 submits "
    "an application snapshot and revision; process 4 ranks active applications; process 5 records "
    "a review or recruitment decision; process 6 produces aggregate audit and evaluation reports. "
    "D1 stores users, sessions and invitations; D2 stores profiles and profile versions; D3 stores "
    "jobs and publication records; D4 stores applications and revisions; D5 stores runs, reviews "
    "and decisions; D6 stores audit attributes, audit events and evaluation records. The separation "
    "between D5 and D6 is the data-flow expression of the ranking/audit boundary.",
)
add_figure(doc, "dfd_level1.png", "Figure 3.3: Level-1 data-flow diagram")

add_body(
    doc,
    "Figure 3.4 shows the principal persistent classes. User, Candidate, ProfileVersion, Job, "
    "Application, ApplicationVersion, Run, Review, RecruitmentDecision and DecisionEvidence form "
    "the operational core. AuditAttribute, AuditLog and Evaluation sit in a separate audit and "
    "evaluation context. The diagram uses application-level references rather than claiming that "
    "every link is a declared foreign-key constraint. The one-application-per-candidate-per-job "
    "rule is enforced by a unique constraint; the remaining links are resolved by the application "
    "and checked by role-aware queries.",
)
add_page_section(doc, landscape=True)
add_figure(
    doc,
    "class_diagram.png",
    "Figure 3.4: Class diagram of the persistent domain",
    max_width_cm=25.0,
    max_height_cm=15.5,
)
add_page_section(doc, landscape=False)

add_body(
    doc,
    "Figure 3.5 is a sequence diagram for the main workflow. A candidate selects a saved profile "
    "and applies; React sends a POST request to the job application endpoint; FastAPI loads the "
    "profile, job and publication state; the database returns the profile snapshot and active "
    "status; the application and its first version are inserted; the candidate receives a 201 "
    "response. A recruiter then opens the applicants and starts a run. FastAPI loads active "
    "application snapshots, calls the matching service, receives scores and requirement evidence, "
    "inserts an immutable run snapshot and returns the saved ranking. The dashed responses show "
    "that the browser never writes directly to the database.",
)
add_figure(doc, "sequence_diagram.png", "Figure 3.5: Sequence diagram for application and matching")

add_body(
    doc,
    "Figure 3.6 is the application state chart. A newly submitted application is active. A "
    "recruiter can open it for review, after which it may be accepted for the next stage or "
    "rejected. A decision can be revised, which appends a new revision and new evidence rather "
    "than rewriting the previous one. Withdrawn is retained as a historical state for older "
    "records; the current withdrawal endpoint returns HTTP 410, and the active interface does not "
    "offer withdrawal. The state model is intentionally small: it describes the application "
    "lifecycle, not an employment contract or an automated hiring decision.",
)
add_figure(doc, "state_chart.png", "Figure 3.6: State chart for a job application")

add_body(
    doc,
    "Figure 3.7 is the activity diagram. A user signs in and resolves a role; a candidate adds or "
    "corrects profile evidence; the system previews extraction and evidence passages; the user "
    "either accepts the evidence or returns to correction. After a profile version is saved, a "
    "recruiter publishes a job, a candidate applies with a snapshot, and the recruiter ranks active "
    "submitted snapshots. The run is saved with immutable evidence. The recruiter records a "
    "decision revision, while an auditor can independently review the aggregate cohort report and "
    "audit events. The loop on the left is important: extraction is treated as a draft that a "
    "human can correct, not as an authoritative reading of the document.",
)
add_figure(doc, "activity_diagram.png", "Figure 3.7: Activity diagram from evidence preparation to audit")

add_body(
    doc,
    "Taken together, the models describe the same system at different levels of abstraction. The "
    "architecture shows the trust boundaries; the data-flow diagrams show the movement of "
    "information; the class diagram shows the durable records; the sequence and state models show "
    "time and lifecycle; and the activity model shows the human workflow. This redundancy is "
    "useful for review because a weakness in one view, such as an unclear ownership check, should "
    "be visible as a missing control in another.",
)

# Chapter 4 -------------------------------------------------------------------
add_heading(doc, "CHAPTER 4  IMPLEMENTATION", 1)
add_heading(doc, "4.1 Development Environment and Technology Stack", 2, page_break=False)
add_body(
    doc,
    "The prototype was implemented and verified on a Windows development laptop with Python "
    "3.11.9 and Node.js 24.15.0. The backend uses FastAPI 0.162.7, Pydantic 2.14.3, SQLAlchemy "
    "2.1.8 and scikit-learn 1.9.1. The frontend uses React 19, TypeScript 5.7 and Vite 6. SQLite "
    "is the default database; a PostgreSQL URL can be supplied through DATABASE_URL. Playwright "
    "1.56 drives the browser tests in an installed Google Chrome. A pinned local "
    "all-MiniLM-L6-v2 model is available for the optional semantic path.",
)

add_table(
    doc,
    "Table 4.1: Verified development stack",
    ["Layer", "Technology", "Role in the prototype"],
    [
        ["Runtime", "Python 3.11.9", "Backend, matching, audit arithmetic"],
        ["API", "FastAPI 0.162.7, Pydantic 2.14.3", "Routes, validation, sessions and role dependencies"],
        ["Persistence", "SQLAlchemy 2.1.8, SQLite", "Records, versions, snapshots and events"],
        ["Matching", "scikit-learn 1.9.1", "TF-IDF, cosine similarity, evaluation metrics"],
        ["Optional model", "all-MiniLM-L6-v2 (pinned local revision)", "Semantic alignment when explicitly configured"],
        ["Frontend", "React 19, TypeScript 5.7, Vite 6", "Role-specific single-page interface"],
        ["Verification", "pytest, Playwright 1.56, Chrome", "API, calculation and browser journeys"],
    ],
    [3.2, 5.6, 6.8],
    font_size=9.0,
)

add_heading(doc, "4.2 Frontend Implementation", 2, page_break=False)
add_body(
    doc,
    "The frontend is a role-aware single-page application. Sign-in and registration are public; "
    "after authentication, the server-assigned role determines the navigation and the available "
    "screens. Candidates see an overview, their owned profiles, published opportunities and their "
    "applications. Recruiters see an overview, jobs, the candidate library, matching evidence, "
    "applications and the evaluation page. Auditors see an aggregate audit report and the event "
    "log. The interface mirrors the server boundaries, but it does not replace them: every "
    "protected request is checked again by FastAPI.",
)
add_body(
    doc,
    "Shared components provide forms, notices, dialogs, pagination and evidence chips. The API "
    "client is typed, centralises error handling and uses AbortController to prevent a superseded "
    "request from replacing a newer result. List state is held in the query string so that a page "
    "or search can be reloaded or shared. Unsaved forms use a confirmation dialog and intercept "
    "browser-back navigation where appropriate. Error messages preserve the user's input and "
    "provide a recovery action rather than clearing the form.",
)
add_body(
    doc,
    "The candidate profile editor shows the extracted text, warnings and recognised skills before "
    "saving. A version conflict is displayed as a conflict rather than silently overwriting a "
    "newer profile. The recruiter's matching screen shows the score, method, profile version and "
    "component breakdown; opening evidence reveals the requirement-to-passage ledger. The "
    "application review screen loads the exact submitted snapshot and the saved matching evidence, "
    "and the decision form requires a revision. The auditor screen exposes a cutoff control, group "
    "counts, rates, intervals, suppression messages and a JSON export. The layout was checked at "
    "desktop and 390-pixel mobile widths.",
)

add_heading(doc, "4.3 Backend and Data Implementation", 2, page_break=False)
add_body(
    doc,
    "The backend is split into backend/app.py, backend/advanced.py and backend/matching.py. The "
    "first module owns the core models, authentication, invitations, jobs, profiles, parsing, "
    "matching runs, reviews and audit events. The second adds publications, applications, "
    "recruitment decisions, decision evidence, snapshot comparisons and the evaluation API. The "
    "third contains the skill vocabulary, context rules, scoring, Wilson intervals and the "
    "aggregate fairness calculation. backend/invite.py is a local administrator command for "
    "creating expiring, email-bound invitations.",
)

add_table(
    doc,
    "Table 4.2: Backend modules and responsibilities",
    ["Module", "Responsibility", "Representative records"],
    [
        ["backend/app.py", "Auth, invitations, jobs, profiles, parsing, runs, reviews, audit", "User, LoginSession, Invitation, Candidate, ProfileVersion, Job, Run, Review, AuditLog"],
        ["backend/advanced.py", "Publications, applications, decisions, evidence, comparisons, evaluations", "Publication, Application, ApplicationVersion, RecruitmentDecision, DecisionEvidence, Evaluation"],
        ["backend/matching.py", "Vocabulary, context rules, scoring, intervals, fairness arithmetic", "In-memory results saved inside a Run"],
        ["backend/invite.py", "Local administrator invitation CLI", "Invitation"],
    ],
    [3.7, 8.3, 3.8],
    font_size=8.8,
)

add_body(
    doc,
    "The core workflow is transactional. A candidate application inserts an Application row and "
    "an ApplicationVersion row in one transaction. The unique constraint on job and owner prevents "
    "duplicate active applications. A recruiter matching request loads active applications, builds "
    "profile snapshots and calls the matcher outside the database query, then inserts a Run with "
    "the complete result JSON. A recruitment decision checks the current revision, appends a new "
    "RecruitmentDecision, appends DecisionEvidence linked to the run and updates the application "
    "status. A stale revision receives a conflict. This design keeps the submitted evidence and "
    "the saved score immutable while allowing the decision to evolve.",
)
add_body(
    doc,
    "The implementation also includes a synthetic evaluation path. A recruiter or auditor can "
    "load a JSON dataset of queries, fictional profiles and relevance grades, choose k, and run "
    "TF-IDF-only or TF-IDF plus the configured local semantic model. The evaluator computes NDCG, "
    "recall and precision per query, averages them across queries and stores the report. The "
    "fixture shipped with the project is a smoke test, not a representative benchmark; its purpose "
    "is to make the evaluation mechanics inspectable and repeatable.",
)
add_body(
    doc,
    "The demo seed creates three accounts, three jobs, twelve fictional profiles, one published "
    "job, one candidate application and two saved matching runs: a legacy all-profile run and a "
    "scoped active-application run. It creates no reviews, so the reviewer workflow starts from a "
    "clean state. The seed runs only when DEMO_MODE is enabled and the user table is empty. The "
    "seeded records are fictional and are labelled as sample data in the interface.",
)

add_heading(doc, "4.4 Security, Privacy and Role Controls", 2, page_break=False)
add_body(
    doc,
    "Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes with 310,000 iterations. A "
    "successful login creates a random opaque token; only its SHA-256 hash and an eight-hour expiry "
    "are stored. The browser receives an HttpOnly, SameSite=Strict cookie. Logout removes the "
    "stored session. Role and ownership checks are dependencies on protected routes, not merely "
    "hidden interface controls. A candidate cannot read another owner's profile; a recruiter "
    "cannot read the auditor report; an auditor cannot retrieve raw profile text or individual "
    "ranking snapshots.",
)
add_body(
    doc,
    "Recruiter and auditor registration requires a single-use invitation bound to the same "
    "normalised email and role. The invitation token is random, stored only as a hash, expires "
    "after a configurable interval (24 hours by default, maximum 168 hours) and is consumed by a "
    "conditional update. A used, expired, wrong-email or wrong-role invitation is rejected. The "
    "invitation command is a local administrator tool; no public invitation-creation endpoint is "
    "exposed. Candidate registration is direct but still validates email format, duplicate "
    "accounts, password confirmation and a minimum password strength.",
)
add_body(
    doc,
    "The API middleware rejects mutation requests from an unapproved Origin, limits request bodies "
    "to 3 MB and sets nosniff, frame-denial, referrer and no-store headers. Uploads are limited to "
    "2 MB, PDFs to 50 pages and DOCX archives to a bounded expanded size. These controls reduce "
    "obvious abuse but are not a malware sandbox, a production identity provider or a complete "
    "privacy programme. Original uploads are not retained; confirmed text is stored locally. "
    "Retention, deletion, consent and organisation-level isolation remain future work.",
)
add_body(
    doc,
    "Audit attributes are stored separately and are never inputs to the matcher. The auditor "
    "report exposes aggregate counts and rates, not individual resumes or ranking snapshots. "
    "Groups smaller than five are suppressed. The interface labels the cohort as synthetic and "
    "states that the labels are not demographic identities or qualification labels. These choices "
    "do not prove fairness; they prevent a small synthetic demonstration from being presented as "
    "one.",
)

add_heading(doc, "4.5 Verification and Results", 2, page_break=False)
add_body(
    doc,
    "Verification combines calculation tests, API integration tests and production-build browser "
    "journeys. The backend suite uses temporary databases, so assertions do not depend on the live "
    "workspace. The browser suite starts its own server on port 8001 with a disposable database and "
    "an explicit allowed origin. The live demo on port 8000 is preserved. Type checking, linting, "
    "formatting and the production build are checked separately.",
)

add_table(
    doc,
    "Table 4.3: Verification summary",
    ["Check", "Recorded result", "What it establishes"],
    [
        ["Backend and API suite", "26 tests passed", "Authentication, ownership, roles, parsing, version conflicts, snapshots, reviews, invitations, decisions, audit suppression, evaluation"],
        ["Production-build browser suite", "9 journeys passed", "Registration for three roles, job creation/editing, profile upload and correction, matching, evidence review, application decision, audit cutoff/export, mobile layout"],
        ["TypeScript type checking", "Passed", "Frontend types compile against the current API shapes"],
        ["ESLint", "Passed with no warnings", "Configured source rules are satisfied"],
        ["Vite production build", "Passed", "The production bundle can be generated"],
        ["Formatting and UI audit", "Passed", "Prettier check and strict project UI audit completed"],
    ],
    [4.2, 4.1, 7.5],
    font_size=8.8,
)

add_body(
    doc,
    "The backend tests exercise successful and rejected workflows. They cover unauthenticated "
    "requests, candidate ownership, recruiter/auditor separation, skill normalisation and "
    "unsupported skills, required/preferred overlap, profile creation and stale-version conflicts, "
    "immutable historical evidence, score arithmetic, mandatory review reasons, invitation rules, "
    "TXT/DOCX/PDF parsing, malformed and oversized files, rejected mutation origins, publication "
    "and application rules, duplicate applications, decision revisions, aggregate-only auditor "
    "access, small-group suppression and the evaluation API. A separate test exercises actual "
    "offline inference with the pinned local semantic model; it is skipped only when the model is "
    "not installed.",
)
add_body(
    doc,
    "The browser journeys exercise the application through the interface rather than through API "
    "calls alone. They register candidate, recruiter and auditor accounts, create and edit a job, "
    "upload a text resume, correct the profile, run matching, inspect evidence and save a review, "
    "submit an application, record a recruitment decision, change the auditor cutoff, export the "
    "report and check the narrow layout. The suite also checks that invalid credentials and invalid "
    "forms preserve entered values and that the unsaved-draft dialog behaves correctly.",
)
add_body(
    doc,
    "These results establish that the selected workflows operate as specified in the recorded "
    "environment. They do not establish model accuracy, hiring quality, demographic fairness, "
    "production throughput, complete accessibility conformance or adversarial parser safety. No "
    "representative labelled dataset was supplied, and the evaluation fixture is synthetic. The "
    "report therefore treats the verification as functional evidence for a prototype, not as a "
    "deployment certificate.",
)

# Chapter 5 -------------------------------------------------------------------
add_heading(doc, "CHAPTER 5  CONCLUSION", 1)
add_heading(doc, "5.1 Conclusion", 2, page_break=False)
add_body(
    doc,
    "Candidate Lab implements an evidence-led workflow for candidate matching and human review. "
    "It connects explicit job requirements to resume passages, calculates a visible matching "
    "index, preserves the information used to produce each result and keeps the final decision "
    "with a human reviewer. The main achievement is an integrated, inspectable application rather "
    "than an unsupported claim of automated hiring intelligence.",
)
add_body(
    doc,
    "The prototype brings together a React and TypeScript interface, FastAPI services, "
    "SQLAlchemy persistence, document parsers, a context-aware skill vocabulary and a TF-IDF "
    "matching baseline, with an optional local semantic path. Candidates manage owned profiles and "
    "applications; recruiters publish jobs, inspect evidence and record reasoned decisions; "
    "auditors inspect aggregate reports and activity events. Expiring role invitations and "
    "server-side permission checks support controlled access in the shared local workspace.",
)
add_body(
    doc,
    "Version-conflict handling protects corrections, while immutable profile, application and run "
    "snapshots retain historical explanations. Direct contribution terms clarify why points were "
    "awarded. These features make the software easier to demonstrate and examine, but keyword "
    "evidence and lexical similarity still require contextual interpretation. A profile can mention "
    "a technology without showing proficiency, a parser can miss useful text and a vocabulary gap "
    "can hide relevant experience.",
)
add_body(
    doc,
    "The recorded verification demonstrates selected functional behaviour through 26 backend "
    "tests and 9 browser journeys, together with type checking, linting and a production build. It "
    "does not establish production readiness or predictive quality. The synthetic cohort audit "
    "illustrates rates and uncertainty, but it cannot establish fairness in a real applicant "
    "population. The project therefore treats explainability and fairness as obligations to make "
    "assumptions, evidence and limits visible, not as properties that a single score can certify.",
)
add_body(
    doc,
    "The project provides a coherent foundation for the next stage. That stage should collect "
    "consented annotations, compare lexical and semantic baselines on held-out data, evaluate "
    "relevance and cohort outcomes with uncertainty and harden identity, retention and deployment "
    "operations. Human oversight and accurate communication of limitations remain essential as the "
    "system evolves.",
)

add_heading(doc, "5.2 Future Scope", 2, page_break=False)
future_items = [
    (
        "Validated evaluation. Collect consented resume-job relevance annotations under a "
        "documented rubric, use multiple annotators and report agreement. Split by candidate and "
        "job family to reduce leakage, then compare skill/TF-IDF, semantic and supervised "
        "approaches on held-out data using recall at k, NDCG at k and confidence intervals.",
    ),
    (
        "Extraction and explanation. Evaluate passage extraction independently and add tests for "
        "negation, abbreviations, unsupported skills and document layout. Introduce OCR for "
        "image-only documents through an isolated processing service, and preserve provenance for "
        "the model, data, rubric and vocabulary versions if a learned model is added.",
    ),
    (
        "Fairness and governance. Obtain approved, consented audit attributes without inferring "
        "protected characteristics. Define the target population and valid qualification labels "
        "before selecting fairness measures. Examine intersectional and small-sample effects, "
        "report uncertainty and evaluate any mitigation against relevance and operational "
        "tradeoffs. A single threshold gap should not be treated as proof of fairness.",
    ),
    (
        "Production operations. Add email verification and password recovery, organisation-specific "
        "identity, tenant isolation, database migrations, isolated parsing, monitoring, backups and "
        "retention/deletion workflows that include historical snapshots. Replace process-local "
        "throttles with operational controls and use durable workers if workload requirements "
        "exceed bounded synchronous processing.",
    ),
    (
        "Deployment and usability. Verify the optional PostgreSQL and container path, configure "
        "HTTPS and secure cookies, and deliberately manage sample accounts before any public "
        "hosting. Conduct accessibility testing and usability studies with representative "
        "candidates, recruiters and auditors. Notifications or additional candidate workflows "
        "should be introduced only with clear authorisation and lifecycle rules.",
    ),
]
for index, item in enumerate(future_items, start=1):
    text = item[0] if isinstance(item, tuple) else item
    add_bullet(doc, f"**{text.split('.')[0]}.** {text.split('.', 1)[1].strip()}", number=f"F{index}")

# References ------------------------------------------------------------------
add_heading(doc, "REFERENCES", 1)
add_body(
    doc,
    "The following sources informed the problem framing, the matching baseline, the document "
    "processing pipeline and the audit design. Web documentation was accessed in November 2026.",
    space_after=10,
)
references = [
    (
        "[1] scikit-learn developers, \"Text feature extraction,\" scikit-learn documentation. "
        "[Online]. Available: https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction"
    ),
    (
        "[2] N. Reimers and I. Gurevych, \"Sentence-BERT: Sentence embeddings using Siamese "
        "BERT-networks,\" in Proceedings of EMNLP-IJCNLP, 2019, pp. 3982-3992."
    ),
    (
        "[3] pypdf developers, \"Extract text from a PDF,\" pypdf documentation. [Online]. "
        "Available: https://pypdf.readthedocs.io/en/stable/user/extract-text.html"
    ),
    (
        "[4] python-docx developers, \"python-docx documentation.\" [Online]. Available: "
        "https://python-docx.readthedocs.io/en/latest/"
    ),
    (
        "[5] S. M. Lundberg and S.-I. Lee, \"A unified approach to interpreting model "
        "predictions,\" in Advances in Neural Information Processing Systems, 2017, pp. 4765-4774."
    ),
    (
        "[6] M. Hardt, E. Price, and N. Srebro, \"Equality of opportunity in supervised "
        "learning,\" in Advances in Neural Information Processing Systems, 2016, pp. 3315-3323."
    ),
    (
        "[7] S. Ramirez, \"FastAPI documentation.\" [Online]. Available: "
        "https://fastapi.tiangolo.com/"
    ),
    (
        "[8] Meta Platforms, \"React documentation.\" [Online]. Available: https://react.dev/"
    ),
    (
        "[9] M. Bayer, \"SQLAlchemy documentation.\" [Online]. Available: "
        "https://docs.sqlalchemy.org/"
    ),
    (
        "[10] E. B. Wilson, \"Probable inference, the law of succession, and statistical "
        "inference,\" Journal of the American Statistical Association, vol. 22, no. 158, "
        "pp. 209-212, 1927."
    ),
]
for reference in references:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.9)
    p.paragraph_format.first_line_indent = Cm(-0.9)
    p.paragraph_format.space_after = Pt(7)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    add_rich(p, reference, size=11)

# Proof of publication --------------------------------------------------------
add_heading(doc, "PROOF OF PUBLICATION", 1)
add_body(
    doc,
    "Publication is not claimed at the time of this Stage-1 submission. No paper from this work "
    "has been communicated, accepted or published. This page is intentionally reserved for an "
    "authentic acceptance letter, conference or journal first page, or DOI record once a "
    "publication exists. A placeholder is used instead of a fabricated certificate.",
    space_after=14,
)
proof_table = doc.add_table(rows=1, cols=1)
proof_table.alignment = WD_TABLE_ALIGNMENT.CENTER
proof_table.autofit = False
proof_table.allow_autofit = False
set_table_borders(proof_table, color="8EA9C1", size=8)
proof_cell = proof_table.rows[0].cells[0]
proof_cell.width = Cm(15.4)
set_cell_shading(proof_cell, "F7F9FC")
set_cell_margins(proof_cell, top=180, start=220, bottom=180, end=220)
proof_lines = [
    ("Publication status", "Not yet published or communicated"),
    ("Title", TITLE),
    ("Authors", ", ".join(f"{name} ({roll})" for name, roll in STUDENTS)),
    ("Journal / conference", "To be inserted after acceptance"),
    ("DOI / proof reference", "To be inserted after publication"),
]
first = True
for label, value in proof_lines:
    p = proof_cell.paragraphs[0] if first else proof_cell.add_paragraph()
    first = False
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.2
    add_rich(p, f"**{label}:** {value}", size=11)
note = doc.add_paragraph()
note.paragraph_format.space_before = Pt(14)
note.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
add_rich(
    note,
    "The project team will replace this page with authentic proof if a publication is produced. "
    "The absence of a publication is not treated as a failure of the Stage-1 work; the report "
    "documents the implemented prototype and its verification instead.",
    size=10.5,
    color=MUTED,
    italic=True,
)

# Final document properties and save -----------------------------------------
doc.save(OUT_DOCX)
print(f"Wrote {OUT_DOCX}")
print(f"Paragraphs: {len(doc.paragraphs)}, tables: {len(doc.tables)}")
