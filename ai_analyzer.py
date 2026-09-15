"""
ai_analyzer.py
--------------
Groq-powered document analysis for DocFormat AI.
"""

import json
import re

from groq import Groq

from config import get_benchmark


DISCLAIMER_PREFIX = "💡 [Suggestion]:"


def build_analysis_prompt(
    report_type,
    parsed_document,
    custom_requirements=""
):
    """
    Build the analysis prompt for Groq.
    """

    benchmark = get_benchmark(report_type)

    required_sections = benchmark.get(
        "required_sections",
        []
    )

    prompt = f"""
You are DocFormat AI, an academic and professional document
formatting auditor.

IMPORTANT:
You are providing recommendations, NOT official institutional rules.

Every feedback item MUST be a suggestion or recommendation.

Never present your assessment as an absolute institutional requirement
unless it was explicitly supplied by the user.

REPORT TYPE:
{report_type}

BENCHMARK:
{json.dumps(benchmark, indent=2)}

CUSTOM TEACHER / INSTITUTE REQUIREMENTS:
{custom_requirements if custom_requirements.strip() else "None provided"}

DOCUMENT INFORMATION:

File type:
{parsed_document.get("file_type")}

Page count:
{parsed_document.get("page_count")}

Word count:
{parsed_document.get("word_count")}

Detected fonts:
{json.dumps(parsed_document.get("fonts", {}))}

Detected font sizes:
{json.dumps(parsed_document.get("font_sizes", {}))}

Detected alignments:
{json.dumps(parsed_document.get("alignments", {}))}

Detected line spacing:
{json.dumps(parsed_document.get("line_spacings", []))}

Page numbers detected:
{parsed_document.get("page_numbers_detected")}

Detected sections:
{json.dumps(parsed_document.get("sections", []))}

DOCUMENT TEXT:
{parsed_document.get("text", "")[:18000]}

REQUIRED SECTIONS FOR THIS REPORT TYPE:
{json.dumps(required_sections)}

TASK:

Analyze the document against the selected benchmark.

Check:

1. Font consistency
2. Body font size
3. Heading font size
4. Alignment
5. Line spacing
6. Page numbering
7. Required sections
8. Structural organization
9. References
10. Custom requirements
11. Overall document quality

IMPORTANT:
Do not mark something as missing if it is clearly present under
a different reasonable heading.

For example:
"Findings & Analysis" may satisfy "Findings".
"Final Remarks" may reasonably satisfy "Conclusion".

Use semantic understanding.

Return ONLY valid JSON.

Use this exact structure:

{{
    "overall_score": 0,
    "summary": "",
    "formatting": [
        {{
            "item": "",
            "status": "Good",
            "evidence": "",
            "recommendation": ""
        }}
    ],
    "structure": [
        {{
            "item": "",
            "status": "Present",
            "evidence": "",
            "recommendation": ""
        }}
    ],
    "missing_sections": [],
    "custom_requirements": [
        {{
            "requirement": "",
            "status": "Not Applicable",
            "evidence": "",
            "recommendation": ""
        }}
    ],
    "priority_fixes": []
}}

Allowed formatting statuses:
Good
Needs Improvement
Not Detected
Not Applicable

Allowed structure statuses:
Present
Needs Improvement
Missing
Not Detected
Not Applicable

Every recommendation must be phrased as a suggestion.
"""


    return prompt


def clean_json_response(response_text):
    """
    Remove markdown code fences if the model returns them.
    """

    text = response_text.strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return text.strip()


def enforce_disclaimer(text):
    """
    Ensure every recommendation starts with a disclaimer prefix.
    """

    if not text:
        return f"{DISCLAIMER_PREFIX} No specific recommendation was generated."

    prefixes = [
        "💡 [Suggestion]:",
        "📌 [Recommended Addition]:"
    ]

    if any(text.strip().startswith(prefix) for prefix in prefixes):
        return text.strip()

    return f"{DISCLAIMER_PREFIX} {text.strip()}"


def enforce_recommendations(data):
    """
    Apply disclaimer tone to all recommendation fields.
    """

    if "formatting" in data:
        for item in data["formatting"]:
            if "recommendation" in item:
                item["recommendation"] = enforce_disclaimer(
                    item["recommendation"]
                )

    if "structure" in data:
        for item in data["structure"]:
            if "recommendation" in item:
                item["recommendation"] = enforce_disclaimer(
                    item["recommendation"]
                )

    if "custom_requirements" in data:
        for item in data["custom_requirements"]:
            if "recommendation" in item:
                item["recommendation"] = enforce_disclaimer(
                    item["recommendation"]
                )

    if "priority_fixes" in data:
        data["priority_fixes"] = [
            enforce_disclaimer(item)
            for item in data["priority_fixes"]
        ]

    if "summary" in data:
        data["summary"] = enforce_disclaimer(
            data["summary"]
        )

    return data


def analyze_document(
    api_key,
    report_type,
    parsed_document,
    custom_requirements=""
):
    """
    Send the document analysis request to Groq.
    """

    if not api_key:
        raise ValueError(
            "Groq API key is missing."
        )

    client = Groq(api_key=api_key)

    prompt = build_analysis_prompt(
        report_type=report_type,
        parsed_document=parsed_document,
        custom_requirements=custom_requirements
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful document-formatting auditor. "
                    "Return valid JSON only."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        response_format={
            "type": "json_object"
        }
    )

    raw_response = response.choices[0].message.content

    cleaned_response = clean_json_response(
        raw_response
    )

    try:
        data = json.loads(cleaned_response)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"AI returned invalid JSON: {exc}"
        )

    return enforce_recommendations(data)
