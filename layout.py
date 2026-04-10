"""Layout configuration and styling for AI Smart Study Planner."""

import streamlit as st

# Status and icon definitions
STATUS_OPTIONS = ["Not Started", "In Progress", "Blocked", "Completed"]
STATUS_ICONS = {
    "Not Started": "🟡",
    "In Progress": "🔵",
    "Blocked": "🔴",
    "Completed": "✅",
}
STATUS_PROGRESS = {
    "Not Started": 0,
    "In Progress": 50,
    "Blocked": 25,
    "Completed": 100,
}
STATUS_LABELS = [f"{STATUS_ICONS[status]} {status}" for status in STATUS_OPTIONS]


def configure_page() -> None:
    """Configure Streamlit page settings and apply custom styling."""
    st.set_page_config(page_title="AI Smart Study Planner", layout="wide")

    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 0.8rem;
            padding-bottom: 0.1rem;
            max-width: 100%;
        }
        h1 {
            margin-bottom: 0.1rem;
            margin-top: 0rem;
            font-size: 1.5rem;
            line-height: 1.2;
        }
        h3 {
            margin-top: 0.02rem;
            margin-bottom: 0.02rem;
            font-size: 0.92rem;
        }
        .stForm {
            padding: 0.15rem;
            border: none;
            gap: 0;
        }
        .stTextInput, .stSelectbox, .stSlider, .stDateInput {
            margin-bottom: 0.02rem;
        }
        [data-testid="stVerticalBlock"] > div {
            gap: 0.02rem;
        }
        label, .stMarkdown, .stCaption {
            font-size: 0.84rem !important;
        }
        .stTextInput input,
        .stDateInput input,
        .stNumberInput input,
        .stSelectbox [data-baseweb="select"] > div {
            min-height: 1.95rem !important;
            font-size: 0.86rem !important;
        }

        div.stButton > button,
        div.stFormSubmitButton > button {
            padding: 0.24rem 0.75rem !important;
            font-size: 0.86rem !important;
            min-height: 2.05rem !important;
            line-height: 1.1 !important;
            border-radius: 0.35rem !important;
        }

        div.stButton > button p,
        div.stFormSubmitButton > button p {
            font-size: 0.86rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
