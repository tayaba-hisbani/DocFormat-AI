"""
doc_parser.py
-------------
Document parsing utilities for PDF and DOCX files.
"""

import io
import re
from collections import Counter

import pdfplumber
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def normalize_font_name(font_name):
    """
    Normalize font names for easier comparison.
    """
    if not font_name:
        return None

    return str(font_name).strip()


def alignment_name(alignment):
    """
    Convert python-docx alignment values to readable names.
    """
    mapping = {
        WD_ALIGN_PARAGRAPH.LEFT: "Left",
        WD_ALIGN_PARAGRAPH.CENTER: "Center",
        WD_ALIGN_PARAGRAPH.RIGHT: "Right",
        WD_ALIGN_PARAGRAPH.JUSTIFY: "Justified",
    }

    return mapping.get(alignment, "Unknown")


def detect_sections(text):
    """
    Detect common academic/report sections from extracted text.
    """
    section_keywords = [
        "abstract",
        "executive summary",
        "introduction",
        "literature review",
        "methodology",
        "method",
        "system design",
        "implementation",
        "results",
        "findings",
        "discussion",
        "recommendations",
        "conclusion",
        "references",
        "bibliography",
        "table of contents",
    ]

    text_lower = text.lower()

    detected = []

    for section in section_keywords:
        if section in text_lower:
            detected.append(section.title())

    return sorted(set(detected))


def detect_page_numbers(text):
    """
    Heuristic page-number detection.

    This is intentionally conservative because PDF/DOCX structures
    do not always expose footer information consistently.
    """
    patterns = [
        r"\bpage\s+\d+\b",
        r"\b\d+\s+of\s+\d+\b",
        r"^\s*\d+\s*$"
    ]

    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            return True

    return False


# ---------------------------------------------------------
# DOCX parsing
# ---------------------------------------------------------

def parse_docx(file_bytes):
    """
    Parse a DOCX document.
    """

    document = Document(io.BytesIO(file_bytes))

    full_text = []

    fonts = []
    font_sizes = []
    alignments = []
    line_spacings = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            full_text.append(text)

        alignment = alignment_name(paragraph.alignment)

        if text:
            alignments.append(alignment)

        if paragraph.paragraph_format.line_spacing:
            line_spacings.append(
                str(paragraph.paragraph_format.line_spacing)
            )

        for run in paragraph.runs:

            if not run.text.strip():
                continue

            if run.font.name:
                fonts.append(
                    normalize_font_name(run.font.name)
                )

            if run.font.size:
                # Convert EMU/Length to points
                try:
                    size = round(
                        run.font.size.pt,
                        1
                    )
                    font_sizes.append(size)
                except Exception:
                    pass

    text = "\n".join(full_text)

    font_counts = Counter(fonts)
    size_counts = Counter(font_sizes)
    alignment_counts = Counter(alignments)

    return {
        "file_type": "DOCX",
        "text": text,
        "page_count": None,
        "fonts": dict(font_counts),
        "font_sizes": dict(size_counts),
        "alignments": dict(alignment_counts),
        "line_spacings": line_spacings,
        "page_numbers_detected": detect_page_numbers(text),
        "sections": detect_sections(text),
        "character_count": len(text),
        "word_count": len(text.split()),
    }


# ---------------------------------------------------------
# PDF parsing
# ---------------------------------------------------------

def parse_pdf(file_bytes):
    """
    Parse a PDF using pdfplumber.
    """

    pages_data = []
    full_text = []

    fonts = []
    font_sizes = []
    alignments = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:

        page_count = len(pdf.pages)

        for page in pdf.pages:

            text = page.extract_text() or ""

            if text:
                full_text.append(text)

            pages_data.append({
                "page_number": page.page_number,
                "text": text,
            })

            # Extract character-level font information where available
            try:
                chars = page.chars

                for char in chars:

                    font_name = char.get("fontname")
                    size = char.get("size")

                    if font_name:
                        fonts.append(
                            normalize_font_name(font_name)
                        )

                    if size:
                        try:
                            font_sizes.append(
                                round(float(size), 1)
                            )
                        except Exception:
                            pass

            except Exception:
                pass

    text = "\n".join(full_text)

    # PDF alignment detection is heuristic.
    # We avoid claiming exact alignment when it cannot be reliably determined.
    alignment_counts = {}

    return {
        "file_type": "PDF",
        "text": text,
        "page_count": page_count,
        "fonts": dict(Counter(fonts)),
        "font_sizes": dict(Counter(font_sizes)),
        "alignments": alignment_counts,
        "line_spacings": [],
        "page_numbers_detected": detect_page_numbers(text),
        "sections": detect_sections(text),
        "character_count": len(text),
        "word_count": len(text.split()),
        "pages": pages_data,
    }


# ---------------------------------------------------------
# Main parser
# ---------------------------------------------------------

def parse_document(file_bytes, file_name):
    """
    Automatically select the correct parser.
    """

    extension = file_name.lower().split(".")[-1]

    if extension == "docx":
        return parse_docx(file_bytes)

    if extension == "pdf":
        return parse_pdf(file_bytes)

    raise ValueError(
        "Unsupported file format. Please upload a PDF or DOCX file."
    )
