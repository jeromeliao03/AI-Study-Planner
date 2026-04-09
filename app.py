import os

import pandas as pd
import streamlit as st
from pandas.errors import EmptyDataError

from calendar_ui import render_month_calendar
from scheduler import calculate_Task_priority, generate_calendar
from layout import (
    configure_page,
    STATUS_OPTIONS,
    STATUS_ICONS,
    STATUS_PROGRESS,
    STATUS_LABELS,
)

configure_page()

st.title("AI Smart Study Planner")

FILE = "data.csv"
COLUMNS = ["tasks", "deadline", "difficulty", "hours", "priority", "status"]

if os.path.exists(FILE):
    try:
        if os.path.getsize(FILE) == 0:
            df = pd.DataFrame(columns=COLUMNS)
        else:
            df = pd.read_csv(FILE)
    except (EmptyDataError, pd.errors.ParserError):
        df = pd.DataFrame(columns=COLUMNS)
else:
    df = pd.DataFrame(columns=COLUMNS)

for col in COLUMNS:
    if col not in df.columns:
        df[col] = pd.NA

df = df[COLUMNS]

total_tasks = len(df)
completed_tasks = len(df[df["status"].fillna("") == "Completed"])
progress = (completed_tasks / total_tasks) if total_tasks > 0 else 0

progress_col, stats_col = st.columns([2, 3], gap="small")
with progress_col:
    st.progress(progress)
with stats_col:
    st.caption(f"{completed_tasks} / {total_tasks} tasks completed")

left_col, right_col = st.columns([0.7, 1.3], gap="small")

with left_col:
    st.subheader("Add Task")
    with st.form("add_task_form", clear_on_submit=True):
        task_name = st.text_input("Task Name")
        deadline = st.date_input("Deadline")
        form_col_1, form_col_2 = st.columns(2, gap="small")
        with form_col_1:
            difficulty = st.slider("Difficulty", 1, 10, 5)
        with form_col_2:
            hours = st.slider("Hours", 1, 20, 2)
        status = st.selectbox("Task Status", STATUS_OPTIONS)
        add_clicked = st.form_submit_button("Add Task", use_container_width=True)

    if add_clicked:
        priority = calculate_Task_priority(str(deadline), difficulty, hours)
        new_row = {
            "tasks": task_name,
            "deadline": str(deadline),
            "difficulty": difficulty,
            "hours": hours,
            "priority": priority,
            "status": status,
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(FILE, index=False)
        st.rerun()

    st.subheader("Delete Tasks")
    if not df.empty:
        task_to_delete = st.selectbox(
            "Select a task to delete",
            df["tasks"].fillna("Unnamed Task").unique(),
            key="delete_task_picker",
        )
        if st.button("Delete Selected", use_container_width=True):
            df = df[df["tasks"] != task_to_delete]
            df.to_csv(FILE, index=False)
            st.rerun()
    else:
        st.caption("No tasks available to delete.")

    st.subheader("Tasks")
    filter_status = st.selectbox(
        "Filter Tasks",
        ["All", *STATUS_OPTIONS],
        key="task_filter_status",
    )

    if filter_status != "All":
        filtered_df = df[df["status"].fillna("Not Started") == filter_status]
    else:
        filtered_df = df

    if not filtered_df.empty:
        display_df = filtered_df.sort_values("priority", ascending=False).copy()
        display_df["status"] = display_df["status"].fillna("Not Started")
        display_df["tasks"] = display_df["tasks"].fillna("Unnamed Task")
        display_df["status_label"] = display_df["status"].map(lambda s: f"{STATUS_ICONS.get(s, '🟡')} {s}")
        display_df["progress"] = display_df["status"].map(lambda s: STATUS_PROGRESS.get(s, 0))
        table_height = min(140, max(60, 28 * (len(display_df) + 1)))

        edited_df = st.data_editor(
            display_df[["tasks", "deadline", "priority", "progress", "status_label"]],
            column_config={
                "tasks": st.column_config.TextColumn("Task", width="medium"),
                "deadline": st.column_config.DateColumn("Deadline", width="small", format="YYYY-MM-DD"),
                "priority": st.column_config.NumberColumn("Priority", width="small", format="%.2f"),
                "progress": st.column_config.ProgressColumn(
                    "Progress",
                    min_value=0,
                    max_value=100,
                    format="%d%%",
                    width="small",
                ),
                "status_label": st.column_config.SelectboxColumn(
                    "Status",
                    options=STATUS_LABELS,
                    required=True,
                    width="small",
                ),
            },
            disabled=["tasks", "deadline", "priority", "progress"],
            use_container_width=True,
            hide_index=True,
            height=table_height,
            key="task_status_editor",
        )

        status_changed = edited_df["status_label"] != display_df["status_label"]
        if status_changed.any():
            updated_status = edited_df.loc[status_changed, "status_label"].str.replace(r"^[^ ]+ ", "", regex=True)
            df.loc[edited_df.index[status_changed], "status"] = updated_status
            df.to_csv(FILE, index=False)
            st.rerun()
    elif df.empty:
        st.info("No tasks yet. Add one above.")
    else:
        st.info("No tasks match the current filter.")

with right_col:
    st.subheader("Calendar")
    calendar_df = generate_calendar(df)
    if not calendar_df.empty:
        render_month_calendar(calendar_df.sort_values("Date"))
    else:
        st.info("No tasks available to show in calendar view.")
