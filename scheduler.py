from datetime import datetime, timedelta
import pandas as pd 

def calculate_Task_priority(deadline, difficulty, hours):
    today = datetime.today()
    deadline_date = datetime.strptime(deadline, "%Y-%m-%d")

    days_left = (deadline_date - today).days

    if days_left <= 0:
        days_left = 1
    
    #Priority formula 
    priority = (difficulty * hours) / days_left
    return round(priority, 2)

def generate_calendar(df):
    today = datetime.today()
    calendar = []

    for _, row in df.iterrows():
        deadline = datetime.strptime(str(row["deadline"]), "%Y-%m-%d")
        days_left = (deadline - today).days

        if days_left <= 0:
            days_left = 1

        hours_per_day = row["hours"] / days_left

        for i in range(days_left):
            day = today + timedelta(days = i)

            calendar.append({
                "Date": day.strftime("%Y-%m-%d"),
                "Task": row["tasks"],
                "Study Hours": round(hours_per_day, 2)
            })
    return pd.DataFrame(calendar)
    
    