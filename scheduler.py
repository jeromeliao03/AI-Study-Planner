from datetime import datetime, timedelta
import pandas as pd 

def calculate_Task_priority(deadline, difficulty, hours):
    today = datetime.today().date()
    deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()

    days_left = (deadline_date - today).days

    if days_left <= 0:
        days_left = 1
    
    #Priority formula 
    priority = (difficulty * hours) / days_left
    return round(priority, 2)

def recompute_priorities(df, today = None):
    
    updated = df.copy()
    reference_date = today or datetime.today().date()

    def _priority_from_row(row):
        deadline_val = pd.to_datetime(row["deadline"], errors="coerce").date() if pd.notnull(row["deadline"]) else reference_date
        difficulty_val = row["difficulty"] if pd.notnull(row["difficulty"]) else 1
        hours_val = row["hours"] if pd.notnull(row["hours"]) else 1

        if pd.isna(deadline_val) or pd.isna(difficulty_val) or pd.isna(hours_val):
            return row.get("priority", 0)
        
        days_left = (deadline_val - reference_date).days
        if days_left <= 0:
            days_left = 1
        
        priority = (float(difficulty_val) * float(hours_val)) / days_left
        return round(priority, 2)
    
    updated["priority"] = updated.apply(_priority_from_row, axis=1)
    return updated

def generate_calendar(df):
    today = datetime.today().date()
    calendar = []

    for _, row in df.iterrows():
        deadline = datetime.strptime(str(row["deadline"]), "%Y-%m-%d").date()
        days_left = (deadline - today).days

        # Skip overdue tasks in forward-looking schedule generation.
        if days_left < 0:
            continue

        # Include the deadline day itself so due dates are visible on calendar.
        day_count = days_left + 1

        hours_per_day = row["hours"] / day_count

        for i in range(day_count):
            day = today + timedelta(days = i)

            calendar.append({
                "Date": day.strftime("%Y-%m-%d"),
                "Task": row["tasks"],
                "Study Hours": round(hours_per_day, 2),
                "Deadline": deadline.strftime("%Y-%m-%d"),
                "Is_Due_Date": day.strftime("%Y-%m-%d") == deadline.strftime("%Y-%m-%d"),
            })
    return pd.DataFrame(calendar)
    
def generate_rescheduled_calendar(df, missed_dates=None, max_daily_hours=4.0):
    """Redistribute task hours when days are missed, respecting a daily hour cap."""
    today = datetime.today().date()
    calendar = []
    unscheduled = []

    missed_set = set()
    for item in missed_dates or []:
        parsed = pd.to_datetime(item, errors="coerce")
        if pd.notna(parsed):
            missed_set.add(parsed.date())

    try:
        daily_cap = float(max_daily_hours)
    except (TypeError, ValueError):
        daily_cap = 4.0

    if daily_cap <= 0:
        daily_cap = 1.0

    for _, row in df.iterrows():
        deadline_ts = pd.to_datetime(row.get("deadline"), errors="coerce")
        hours_val = pd.to_numeric(row.get("hours"), errors="coerce")
        task_name = row.get("tasks", "Unnamed Task")

        if pd.isna(deadline_ts) or pd.isna(hours_val):
            continue

        deadline = deadline_ts.date()
        total_hours = float(hours_val)

        if total_hours <= 0:
            continue

        days_left = (deadline - today).days
        if days_left < 0:
            continue

        full_range = [today + timedelta(days=i) for i in range(days_left + 1)]
        active_days = [d for d in full_range if d not in missed_set]

        if not active_days:
            unscheduled.append(
                {
                    "Task": task_name,
                    "Unscheduled Hours": round(total_hours, 2),
                    "Reason": "All available days were marked missed.",
                }
            )
            continue

        allocations = {day: 0.0 for day in active_days}
        remaining = total_hours

        # Even redistribution loop with capacity limit.
        while remaining > 1e-9:
            available_days = [d for d in active_days if allocations[d] < daily_cap]
            if not available_days:
                break

            even_share = remaining / len(available_days)
            changed = False

            for day in available_days:
                room = daily_cap - allocations[day]
                add_hours = min(even_share, room)
                if add_hours > 0:
                    allocations[day] += add_hours
                    remaining -= add_hours
                    changed = True

            if not changed:
                break

        if remaining > 1e-6:
            unscheduled.append(
                {
                    "Task": task_name,
                    "Unscheduled Hours": round(remaining, 2),
                    "Reason": "Daily capacity limit reached before deadline.",
                }
            )

        for day, hours in allocations.items():
            if hours <= 0:
                continue
            calendar.append(
                {
                    "Date": day.strftime("%Y-%m-%d"),
                    "Task": task_name,
                    "Study Hours": round(hours, 2),
                    "Deadline": deadline.strftime("%Y-%m-%d"),
                    "Is_Due_Date": day == deadline,
                }
            )

    return pd.DataFrame(calendar), pd.DataFrame(unscheduled)