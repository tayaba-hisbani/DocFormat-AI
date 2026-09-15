"""
app.py
------
DocFormat AI
Production-oriented document formatting and structure auditor.
"""

import os

import streamlit as st
from dotenv import load_dotenv

from config import BENCHMARKS
from doc_parser import parse_document
from ai_analyzer import analyze_document


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="DocFormat AI",
    page_icon="📄",
    layout="wide"
)


# ---------------------------------------------------------
# Styling
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        color: #666;
        margin-bottom: 25px;
    }

    .score-box {
        padding: 20px;
        border-radius: 12px;
        background-color: #f5f5f5;
        text-align: center;
    }

    .recommendation {
        padding: 12px;
        border-radius: 8px;
        background-color: #f8f8f8;
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">📄 DocFormat AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered academic and business document formatting auditor'
    '</div>',
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.header("⚙️ Document Settings")

    report_type = st.selectbox(
        "Document Type",
        list(BENCHMARKS.keys())
    )

    st.divider()

    st.subheader("📋 Custom Requirements")

    custom_requirements = st.text_area(
        "Teacher / Institute Requirements",
        placeholder=(
            "Example:\n"
            "Use Times New Roman 12pt.\n"
            "Use 1.5 line spacing.\n"
            "Use APA 7th edition.\n"
            "Margins should be 1 inch."
        ),
        height=180
    )

    st.divider()

    st.caption(
        "DocFormat AI provides recommendations only. "
        "Always verify your institution's official guidelines."
    )


# ---------------------------------------------------------
# Upload
# ---------------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload your document",
    type=["pdf", "docx"],
    help="Supported formats: PDF and DOCX"
)


if uploaded_file:

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )

    col1, col2, col3 = st.columns(3)

    file_size_mb = (
        uploaded_file.size / (1024 * 1024)
    )

    with col1:
        st.metric(
            "File Type",
            uploaded_file.name.split(".")[-1].upper()
        )

    with col2:
        st.metric(
            "File Size",
            f"{file_size_mb:.2f} MB"
        )

    with col3:
        st.metric(
            "Document Type",
            report_type
        )

    st.divider()

    analyze_button = st.button(
        "🔍 Analyze Document",
        type="primary",
        use_container_width=True
    )

    if analyze_button:

        try:

            with st.spinner(
                "Reading and analyzing your document..."
            ):

                file_bytes = uploaded_file.getvalue()

                parsed_document = parse_document(
                    file_bytes,
                    uploaded_file.name
                )

                api_key = os.getenv(
                    "GROQ_API_KEY"
                )

                if not api_key:
                    st.error(
                        "GROQ_API_KEY is not configured."
                    )
                    st.info(
                        "Add your Groq API key in Streamlit "
                        "Community Cloud Secrets."
                    )
                    st.stop()

                result = analyze_document(
                    api_key=api_key,
                    report_type=report_type,
                    parsed_document=parsed_document,
                    custom_requirements=custom_requirements
                )

            st.success(
                "Analysis completed successfully."
            )

            # -------------------------------------------------
            # Score
            # -------------------------------------------------

            score = result.get(
                "overall_score",
                0
            )

            st.subheader("📊 Overall Score")

            score_col1, score_col2 = st.columns(
                [1, 3]
            )

            with score_col1:

                st.markdown(
                    f"""
                    <div class="score-box">
                        <h1>{score}/100</h1>
                        <p>Overall Document Score</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with score_col2:

                st.write(
                    result.get(
                        "summary",
                        "No summary available."
                    )
                )

            st.divider()

            # -------------------------------------------------
            # Tabs
            # -------------------------------------------------

            tab1, tab2, tab3, tab4, tab5 = st.tabs(
                [
                    "📐 Formatting",
                    "🏗️ Structure",
                    "❌ Missing Sections",
                    "📋 Custom Requirements",
                    "💡 Priority Fixes"
                ]
            )

            # -------------------------------------------------
            # Formatting
            # -------------------------------------------------

            with tab1:

                formatting = result.get(
                    "formatting",
                    []
                )

                if not formatting:
                    st.info(
                        "No formatting findings returned."
                    )

                for item in formatting:

                    status = item.get(
                        "status",
                        "Not Detected"
                    )

                    if status == "Good":
                        icon = "✅"

                    elif status == "Needs Improvement":
                        icon = "⚠️"

                    elif status == "Not Detected":
                        icon = "ℹ️"

                    else:
                        icon = "➖"

                    st.markdown(
                        f"### {icon} {item.get('item', 'Formatting Check')}"
                    )

                    st.write(
                        f"**Status:** {status}"
                    )

                    if item.get("evidence"):
                        st.write(
                            f"**Evidence:** {item['evidence']}"
                        )

                    if item.get("recommendation"):
                        st.info(
                            item["recommendation"]
                        )

                    st.divider()

            # -------------------------------------------------
            # Structure
            # -------------------------------------------------

            with tab2:

                structure = result.get(
                    "structure",
                    []
                )

                for item in structure:

                    status = item.get(
                        "status",
                        "Not Detected"
                    )

                    if status == "Present":
                        icon = "✅"

                    elif status == "Missing":
                        icon = "❌"

                    elif status == "Needs Improvement":
                        icon = "⚠️"

                    else:
                        icon = "ℹ️"

                    st.markdown(
                        f"### {icon} {item.get('item', 'Section')}"
                    )

                    st.write(
                        f"**Status:** {status}"
                    )

                    if item.get("evidence"):
                        st.write(
                            f"**Evidence:** {item['evidence']}"
                        )

                    if item.get("recommendation"):
                        st.info(
                            item["recommendation"]
                        )

                    st.divider()

            # -------------------------------------------------
            # Missing Sections
            # -------------------------------------------------

            with tab3:

                missing = result.get(
                    "missing_sections",
                    []
                )

                if missing:

                    st.warning(
                        "The following sections may need attention:"
                    )

                    for section in missing:
                        st.write(
                            f"• {section}"
                        )

                    st.info(
                        "💡 [Suggestion]: Review these sections "
                        "against your teacher or institute's official "
                        "requirements before making changes."
                    )

                else:

                    st.success(
                        "No potentially missing required sections "
                        "were identified."
                    )

            # -------------------------------------------------
            # Custom Requirements
            # -------------------------------------------------

            with tab4:

                custom_results = result.get(
                    "custom_requirements",
                    []
                )

                if not custom_requirements.strip():

                    st.info(
                        "No custom requirements were provided."
                    )

                else:

                    for item in custom_results:

                        st.markdown(
                            f"### {item.get('requirement', '')}"
                        )

                        st.write(
                            f"**Status:** "
                            f"{item.get('status', 'Not Detected')}"
                        )

                        if item.get("evidence"):
                            st.write(
                                f"**Evidence:** "
                                f"{item['evidence']}"
                            )

                        if item.get("recommendation"):
                            st.info(
                                item["recommendation"]
                            )

                        st.divider()

            # -------------------------------------------------
            # Priority Fixes
            # -------------------------------------------------

            with tab5:

                fixes = result.get(
                    "priority_fixes",
                    []
                )

                if fixes:

                    for index, fix in enumerate(
                        fixes,
                        start=1
                    ):

                        st.markdown(
                            f"### {index}. {fix}"
                        )

                else:

                    st.info(
                        "No priority fixes were returned."
                    )

            # -------------------------------------------------
            # Technical Extraction Details
            # -------------------------------------------------

            with st.expander(
                "🔎 Technical Document Data"
            ):

                st.write(
                    "### Detected Fonts"
                )
                st.json(
                    parsed_document.get(
                        "fonts",
                        {}
                    )
                )

                st.write(
                    "### Detected Font Sizes"
                )
                st.json(
                    parsed_document.get(
                        "font_sizes",
                        {}
                    )
                )

                st.write(
                    "### Detected Alignments"
                )
                st.json(
                    parsed_document.get(
                        "alignments",
                        {}
                    )
                )

                st.write(
                    "### Detected Sections"
                )
                st.write(
                    parsed_document.get(
                        "sections",
                        []
                    )
                )

                st.write(
                    "### Page Numbers Detected"
                )
                st.write(
                    parsed_document.get(
                        "page_numbers_detected"
                    )
                )

        except Exception as error:

            st.error(
                "The document could not be analyzed."
            )

            st.exception(error)


# ---------------------------------------------------------
# Empty state
# ---------------------------------------------------------

else:

    st.info(
        "👆 Upload a PDF or DOCX file to begin."
    )

    st.subheader(
        "What DocFormat AI checks"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            ### 📐 Formatting

            - Font consistency
            - Font sizes
            - Alignment
            - Line spacing
            - Page numbering
            """
        )

    with col2:
        st.markdown(
            """
            ### 🏗️ Structure

            - Required sections
            - Report organization
            - References
            - Missing sections
            """
        )

    with col3:
        st.markdown(
            """
            ### 🤖 AI Recommendations

            - Evidence-based feedback
            - Priority fixes
            - Custom requirements
            - Suggestion-only tone
            """
        )
