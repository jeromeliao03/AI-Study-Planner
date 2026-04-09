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
            padding-top: 1.5rem;
            padding-bottom: 0.2rem;
            max-width: 100%;
        }
        h1 {
            margin-bottom: 0.1rem;
            margin-top: 0rem;
            font-size: 1.8rem;
            line-height: 1.2;
        }
        h3 {
            margin-top: 0.05rem;
            margin-bottom: 0.05rem;
            font-size: 1rem;
        }
        .stForm {
            padding: 0.3rem;
            border: none;
            gap: 0;
        }
        .stTextInput, .stSelectbox, .stSlider, .stDateInput {
            margin-bottom: 0.1rem;
        }
        [data-testid="stVerticalBlock"] > div {
            gap: 0.1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
