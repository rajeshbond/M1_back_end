from datetime import datetime, time, timedelta
from typing import List

from fastapi import HTTPException
import pandas as pd

from app import schemas


def calculate_duration(start: time, end: time) -> float:
    start_dt = datetime.combine(datetime.today(), start)
    end_dt = datetime.combine(datetime.today(), end)
    if end_dt <= start_dt:
        end_dt += timedelta(days=1)
    return (end_dt - start_dt).total_seconds() / 3600

def check_overlap(timings: List[schemas.ShiftTimingCreate]):
    df = pd.DataFrame([t.dict() for t in timings])
    df = df.sort_values(by=["weekday", "shift_start"])
    for day, group in df.groupby("weekday"):
        for i in range(1, len(group)):
            prev = group.iloc[i - 1]
            curr = group.iloc[i]
            if prev.shift_end > curr.shift_start:
                raise HTTPException(400, f"Overlapping shifts on weekday {day}")
