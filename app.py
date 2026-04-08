import streamlit as st
import pandas as pd 
import os 

from pandas.errors import EmptyDataError
from scheduler import calculate_Task_priority, generate_schedule

st.title("AI Smart Study Planner")

FILE = "data.csv"
COLUMNS = ["tasks", "deadline", "difficulty", "hours", "priority"]

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

# Ensure all expected columns exist if a partially valid file is loaded.
for col in COLUMNS:
    if col not in df.columns:
        df[col] = pd.NA

df = df[COLUMNS]

tasks = st.text_input("Task Name")
deadline = st.date_input("Deadline")
difficulty = st.slider("Difficulty (1-10)", 1, 10)
hours = st.slider("Estimated Hours", 1, 20)

if st.button("Add Task"):
    priority = calculate_Task_priority(str(deadline), difficulty, hours)

    new_row = {
        "tasks": tasks,
        "deadline": str(deadline),
        "difficulty": difficulty,
        "hours": hours,
        "priority": priority
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(FILE, index=False)

    st.success("Task saved!")
    
# Display saved tasks
st.subheader("Saved Tasks")
st.dataframe(df.sort_values("priority", ascending=False))

#delete task button
st.subheader("Delete Task")
task_to_delete = st.selectbox("Select Task to Delete", df["tasks"].unique())

if st.button("Delete Task"):
    df = df[df["tasks"] != task_to_delete]
    df.to_csv(FILE, index=False)
    st.success("Task deleted!")

# Generate today's study plan
st.subheader("Today's AI Study Plan")
if st.button("Generate Today's Plan"):
    plan = generate_schedule(df)
    if plan:
        plan_df = pd.DataFrame(plan).rename(
            columns={
                "tasks": "Task",
                "study_today_hours": "Study Today (Hours)",
                "deadline": "Deadline",
            }
        )
        st.table(plan_df)
    else:
        st.info("No tasks available to generate a study plan.")
