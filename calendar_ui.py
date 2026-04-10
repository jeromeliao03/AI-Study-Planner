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
    due_tasks = set(day_info.get("due_tasks", []))
    tooltip_lines = [
        html.escape(f"Date: {day.strftime('%Y-%m-%d')}"),
        html.escape(f"Total: {format_hours(day_info['study_hours'])}"),
        "Tasks:",
    ]

    for idx, task in enumerate(day_info["tasks"], start=1):
        task_text = html.escape(str(task))
        if task in due_tasks:
            tooltip_lines.append(f"{idx}. <span style=\"color:#ff7b7b;font-weight:700;\">{task_text} (DEADLINE)</span>")
        else:
            tooltip_lines.append(f"{idx}. {task_text}")

    return "<br>".join(tooltip_lines)



def render_month_calendar(calendar_df):
    calendar_df = calendar_df.copy()
    calendar_df["Date"] = pd.to_datetime(calendar_df["Date"]).dt.date

    due_tasks_by_date = (
        calendar_df[calendar_df["Is_Due_Date"]]
        .groupby("Date")["Task"]
        .apply(lambda s: list(dict.fromkeys(s.tolist())))
        .to_dict()
    )

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
            "due_tasks": due_tasks_by_date.get(row["Date"], []),
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
        .calendar-tooltip {
            visibility: hidden;
            opacity: 0;
            position: absolute;
            z-index: 999;
            bottom: 105%;
            left: 50%;
            transform: translateX(-50%);
            width: 240px;
            background: #1a1a2e;
            color: #f0f0f0;
            border: 1px solid #ff4444;
            border-radius: 6px;
            padding: 10px;
            font-size: 0.78rem;
            line-height: 1.4;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
            pointer-events: none;
            white-space: normal;
            text-align: left;
            transition: opacity 0.2s ease;
        }
        .calendar-card:hover .calendar-tooltip {
            visibility: visible;
            opacity: 1;
        }
        .calendar-column {
            min-height: 150px;
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
                    st.markdown(f"""
                        <div class="calendar-column" style="border: 1px solid rgba(151, 166, 195, 0.25) !important; border-radius: 10px; padding: 12px; min-height: 140px; background: rgba(19, 26, 42, 0.35);">
                            <div style="font-weight: 700; font-size: 1.1rem;">{day}</div>
                            <div style="font-size: 0.8rem; color: #9aa4b5;">No study</div>
                        </div>
                    """, unsafe_allow_html=True)
                    continue

                task_count = len(day_info["tasks"])
                due_tasks = day_info.get("due_tasks", [])
                top_task = due_tasks[0] if due_tasks else day_info["tasks"][0]
                top_task = shorten_text(top_task)
                remaining = task_count - 1
                is_due_task_preview = bool(due_tasks)
                task_preview = f"{top_task} (+{remaining} more)" if remaining > 0 else top_task
                tooltip = build_tooltip_html(current_date, day_info)

                task_preview_html = html.escape(task_preview)
                if is_due_task_preview:
                    task_preview_html = f"<span style=\"color:#ff7b7b;font-weight:700;\">{task_preview_html}</span>"

                st.markdown(f"""
                    <div class="calendar-card calendar-column" style="border: 1px solid rgba(151, 166, 195, 0.25); background: rgba(19, 26, 42, 0.35); border-radius: 10px; padding: 12px; min-height: 140px; position: relative;">
                        <div style="font-weight: 700; font-size: 1.1rem; margin-bottom: 4px;">{day}</div>
                        <div style="font-size: 0.8rem; color: #9aa4b5; margin-bottom: 6px; line-height: 1.3;">{format_hours(day_info['study_hours'])} | {task_count} task(s)</div>
                        <div style="font-size: 0.85rem; line-height: 1.35;">{task_preview_html}</div>
                        <div class="calendar-tooltip">{tooltip}</div>
                    </div>
                """, unsafe_allow_html=True)
