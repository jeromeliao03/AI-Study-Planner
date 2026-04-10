import os

import pandas as pd
import streamlit as st
from pandas.errors import EmptyDataError

from calendar_ui import render_month_calendar
from scheduler import calculate_Task_priority, generate_calendar, recompute_priorities, generate_rescheduled_calendar
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

refreshed_df = recompute_priorities(df)
if not refreshed_df["priority"].equals(df["priority"]):
    df = refreshed_df
    df.to_csv(FILE, index=False)
else:
    df = refreshed_df

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
        task_col_1, task_col_2 = st.columns(2, gap="small")
        with task_col_1:
            task_name = st.text_input("Task Name")
        with task_col_2:
            deadline = st.date_input("Deadline")
        form_col_1, form_col_2 = st.columns(2, gap="small")
        with form_col_1:
            difficulty = st.slider("Difficulty", 1, 10, 5)
        with form_col_2:
            hours = st.slider("Hours", 1, 20, 2)

        status_label_col, _ = st.columns([3.6, 1.4], gap="small")
        with status_label_col:
            st.markdown("Task Status")

        status_col, add_col = st.columns([3.6, 1.4], gap="small")
        with status_col:
            status = st.selectbox("Task Status", STATUS_OPTIONS, label_visibility="collapsed")
        with add_col:
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
        delete_label_col, _ = st.columns([3.6, 1.4], gap="small")
        with delete_label_col:
            st.markdown("Select a task to delete")

        delete_col, delete_btn_col = st.columns([3.6, 1.4], gap="small")
        with delete_col:
            task_to_delete = st.selectbox(
                "Select a task to delete",
                df["tasks"].fillna("Unnamed Task").unique(),
                key="delete_task_picker",
                label_visibility="collapsed",
            )
        with delete_btn_col:
            delete_clicked = st.button("Delete Selected", use_container_width=True)

        if delete_clicked:
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
        display_df["deadline"] = pd.to_datetime(display_df["deadline"], errors="coerce")
        display_df["status_label"] = display_df["status"].map(lambda s: f"{STATUS_ICONS.get(s, '🟡')} {s}")
        display_df["progress"] = display_df["status"].map(lambda s: STATUS_PROGRESS.get(s, 0))
        table_height = 44 * 6 + 8 if len(display_df) > 5 else None

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
            disabled=["tasks", "priority", "progress"],
            use_container_width=True,
            hide_index=True,
            height=table_height,
            key="task_status_editor",
        )

        status_changed = edited_df["status_label"] != display_df["status_label"]

        original_deadline = pd.to_datetime(display_df["deadline"], errors="coerce")
        edited_deadline = pd.to_datetime(edited_df["deadline"], errors="coerce")
        deadline_changed = edited_deadline != original_deadline

        if status_changed.any() or deadline_changed.any():
            if status_changed.any():
                updated_status = edited_df.loc[status_changed, "status_label"].str.replace(r"^[^ ]+ ", "", regex=True)
                df.loc[edited_df.index[status_changed], "status"] = updated_status

            if deadline_changed.any():
                changed_indices = edited_df.index[deadline_changed]
                updated_deadlines = pd.to_datetime(
                    edited_df.loc[changed_indices, "deadline"],
                    errors="coerce",
                ).dt.strftime("%Y-%m-%d")
                df.loc[changed_indices, "deadline"] = updated_deadlines.values

                for idx in changed_indices:
                    row = df.loc[idx]
                    if pd.isna(row["deadline"]) or pd.isna(row["difficulty"]) or pd.isna(row["hours"]):
                        continue
                    df.loc[idx, "priority"] = calculate_Task_priority(
                        str(row["deadline"]),
                        row["difficulty"],
                        row["hours"],
                    )

            df.to_csv(FILE, index=False)
            st.rerun()
    elif df.empty:
        st.info("No tasks yet. Add one above.")
    else:
        st.info("No tasks match the current filter.")

    st.subheader("Smart Rescheduler")

    if "missed_days" not in st.session_state:
        st.session_state["missed_days"] = []

    rescheduler_col_1, rescheduler_col_2 = st.columns(2, gap="small")
    with rescheduler_col_1:
        missed_day_input = st.date_input("Mark a missed day", key="missed_day_input")
    with rescheduler_col_2:
        max_daily_hours = st.slider(
            "Max study hours/day",
            min_value=1,
            max_value=12,
            value=4,
            key="max_daily_hours_slider",
        )

    action_left, _ = st.columns([1.25, 1], gap="small")
    with action_left:
        btn_col_1, btn_col_2 = st.columns(2, gap="small")
        with btn_col_1:
            if st.button("Add Missed Day", use_container_width=True):
                missed_str = str(missed_day_input)
                if missed_str not in st.session_state["missed_days"]:
                    st.session_state["missed_days"].append(missed_str)

        with btn_col_2:
            if st.button("Clear Missed Days", use_container_width=True):
                st.session_state["missed_days"] = []

    if st.session_state["missed_days"]:
        st.caption("Missed days: " + ", ".join(sorted(st.session_state["missed_days"])))
    else:
        st.caption("No missed days marked.")

    calendar_df, unscheduled_df = generate_rescheduled_calendar(
        df,
        missed_dates=st.session_state["missed_days"],
        max_daily_hours=float(max_daily_hours),
    )

    if not unscheduled_df.empty:
        st.warning("Some hours could not be scheduled before deadline.")
        st.dataframe(unscheduled_df, use_container_width=True, hide_index=True)

with right_col:
    st.subheader("Calendar")
    if not calendar_df.empty:
        render_month_calendar(calendar_df.sort_values("Date"))
    else:
        st.info("No tasks available to show in calendar view.")
