from datetime import datetime, timedelta

def calculate_Task_priority(deadline, difficulty, hours):
    today = datetime.today()
    deadline_date = datetime.strptime(deadline, "%Y-%m-%d")

    days_left = (deadline_date - today).days

    if days_left <= 0:
        days_left = 1
    
    #Priority formula 
    priority = (difficulty * hours) / days_left
    return round(priority, 2)

def generate_schedule(df):
    today = datetime.today()
    schedule = []

    for _, row in df.iterrows():
        deadline = datetime.strptime(str(row["deadline"]), "%Y-%m-%d")
        days_left = (deadline - today).days

        if days_left < 0:
            days_left = 1
        
        hours_per_day = row["hours"] / days_left

        schedule.append({
            "tasks": row["tasks"],
            "study_today_hours": round(hours_per_day, 2),
            "deadline": row["deadline"],
        })
    
    return sorted(schedule, key=lambda x: x["study_today_hours"], reverse=True)



    