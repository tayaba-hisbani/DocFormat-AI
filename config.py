"""
config.py
---------
Configuration and benchmark rules for DocFormat AI.
"""

BENCHMARKS = {
    "Assignment": {
        "description": "Academic assignment formatting benchmark.",
        "fonts": [
            "Calibri",
            "Times New Roman"
        ],
        "body_font_sizes": [11, 12],
        "heading_font_sizes": [12, 13, 14],
        "line_spacing": [
            "1.0",
            "1.15",
            "1.5",
            "double"
        ],
        "alignment": [
            "left",
            "justified"
        ],
        "required_sections": [
            "Title",
            "Questions",
            "Answers",
            "References"
        ],
        "focus": [
            "Title block",
            "Question headers",
            "Concise answers",
            "Consistent font",
            "Reference list"
        ]
    },

    "Project Report": {
        "description": "Academic project/final year project report benchmark.",
        "fonts": [
            "Times New Roman"
        ],
        "body_font_sizes": [12],
        "heading_font_sizes": [14, 16, 18],
        "line_spacing": [
            "1.5",
            "double"
        ],
        "alignment": [
            "justified",
            "left"
        ],
        "required_sections": [
            "Title Page",
            "Abstract",
            "Table of Contents",
            "Introduction",
            "Literature Review",
            "Methodology",
            "System Design",
            "Implementation",
            "Results",
            "Conclusion",
            "References"
        ],
        "focus": [
            "Abstract",
            "Table of Contents",
            "Methodology",
            "System Design",
            "Results",
            "Conclusion",
            "APA/IEEE references",
            "Page numbering"
        ]
    },

    "General / Business Report": {
        "description": "General professional and business report benchmark.",
        "fonts": [
            "Arial",
            "Calibri"
        ],
        "body_font_sizes": [11, 12],
        "heading_font_sizes": [12, 14, 16],
        "line_spacing": [
            "1.0",
            "1.15",
            "1.5"
        ],
        "alignment": [
            "left",
            "justified"
        ],
        "required_sections": [
            "Title",
            "Executive Summary",
            "Introduction",
            "Findings",
            "Recommendations",
            "Conclusion",
            "References"
        ],
        "focus": [
            "Executive Summary",
            "Clean bullet hierarchy",
            "Findings",
            "Actionable recommendations",
            "Page numbers"
        ]
    }
}


DISCLAIMER_PREFIXES = [
    "💡 [Suggestion]:",
    "📌 [Recommended Addition]:"
]


def get_benchmark(report_type):
    """
    Return benchmark configuration for the selected report type.
    """
    return BENCHMARKS.get(report_type, {})


def get_required_sections(report_type):
    """
    Return required sections for a selected report type.
    """
    benchmark = get_benchmark(report_type)
    return benchmark.get("required_sections", [])
