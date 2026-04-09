import calendar
import html
from datetime import datetime

import pandas as pd
import streamlit as st


def format_hours(hours_value):
    whole_hours = int(hours_value)
    minutes = int(round((hours_value - whole_hours) * 60))

    if minutes == 60:
        whole_hours += 1
        minutes = 0

    return f"{whole_hours}h {minutes:02d}m"


def shorten_text(value, max_len=28):
    text = str(value)
    if len(text) <= max_len:
        return text
    return f"{text[:max_len - 1]}..."


def build_tooltip_html(day, day_info):
    tooltip_lines = [
        f"Date: {day.strftime('%Y-%m-%d')}",
        f"Total: {format_hours(day_info['study_hours'])}",
        "Tasks:",
    ]

    for idx, task in enumerate(day_info["tasks"], start=1):
        tooltip_lines.append(f"{idx}. {task}")

    escaped_lines = [html.escape(line) for line in tooltip_lines]
    return "<br>".join(escaped_lines)


def render_month_calendar(calendar_df):
    calendar_df = calendar_df.copy()
    calendar_df["Date"] = pd.to_datetime(calendar_df["Date"]).dt.date

    grouped = (
        calendar_df.groupby("Date", as_index=False)
        .agg(
            {
                "Task": lambda s: list(s),
                "Study Hours": "sum",
            }
        )
    )

    date_to_items = {
        row["Date"]: {
            "tasks": row["Task"],
            "study_hours": row["Study Hours"],
        }
        for _, row in grouped.iterrows()
    }

    month_keys = sorted({(d.year, d.month) for d in grouped["Date"]})
    month_labels = [datetime(y, m, 1).strftime("%B %Y") for y, m in month_keys]
    label_to_month = {label: key for label, key in zip(month_labels, month_keys)}

    selected_month = st.selectbox("Select month", month_labels)
    year, month = label_to_month[selected_month]

    st.markdown(
        """
        <style>
        .calendar-card {
            position: relative;
            border: 1px solid rgba(151, 166, 195, 0.25);
            border-radius: 10px;
            padding: 8px;
            min-height: 120px;
            background: rgba(19, 26, 42, 0.35);
            cursor: help;
            overflow: visible;
        }
        .calendar-day {
            font-weight: 700;
            margin-bottom: 4px;
        }
        .calendar-meta {
            font-size: 0.78rem;
            color: #9aa4b5;
            margin-bottom: 4px;
        }
        .calendar-task {
            font-size: 0.82rem;
            line-height: 1.2;
        }
        .calendar-tooltip {
            visibility: hidden;
            opacity: 0;
            transition: opacity 0.15s ease;
            position: absolute;
            z-index: 999;
            left: 50%;
            bottom: calc(100% + 8px);
            transform: translateX(-50%);
            width: 260px;
            background: #101828;
            color: #f8fafc;
            border: 1px solid rgba(151, 166, 195, 0.45);
            border-radius: 8px;
            padding: 8px 10px;
            font-size: 0.78rem;
            line-height: 1.35;
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.32);
            pointer-events: none;
            text-align: left;
        }
        .calendar-card:hover .calendar-tooltip {
            visibility: visible;
            opacity: 1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"### {datetime(year, month, 1).strftime('%B %Y')}")

    day_headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    header_cols = st.columns(7)
    for idx, day_name in enumerate(day_headers):
        with header_cols[idx]:
            st.markdown(f"**{day_name}**")

    month_matrix = calendar.monthcalendar(year, month)

    for week in month_matrix:
        week_cols = st.columns(7)
        for idx, day in enumerate(week):
            with week_cols[idx]:
                if day == 0:
                    st.markdown(" ")
                    continue

                current_date = datetime(year, month, day).date()
                day_info = date_to_items.get(current_date)

                if not day_info:
                    st.markdown(
                        f"""
                        <div class="calendar-card">
                            <div class="calendar-day">{day}</div>
                            <div class="calendar-meta">No study</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    continue

                task_count = len(day_info["tasks"])
                top_task = html.escape(shorten_text(day_info["tasks"][0]))
                remaining = task_count - 1

                if remaining > 0:
                    task_preview = f"{top_task} (+{remaining} more)"
                else:
                    task_preview = top_task

                tooltip_html = build_tooltip_html(current_date, day_info)

                st.markdown(
                    f"""
                    <div class="calendar-card">
                        <div class="calendar-day">{day}</div>
                        <div class="calendar-meta">{format_hours(day_info['study_hours'])} total | {task_count} task(s)</div>
                        <div class="calendar-task">{task_preview}</div>
                        <div class="calendar-tooltip">{tooltip_html}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
