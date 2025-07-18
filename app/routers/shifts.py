from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta, time
from app import schemas, models, oauth2
from ..database import get_db
import pandas as pd
from ..function import shifts_fn

router = APIRouter(prefix="/shifts/v1", tags=["Shifts"])


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def create_multiple_shifts(
    payload: List[schemas.TenantShiftCreate],
    db: Session = Depends(get_db),
    current_user: models.user = Depends(oauth2.get_current_user)
):
    try:    
        role = db.query(models.role).filter(models.role.id == current_user.role_id).first()

        if role.role not in ["superAdmin", "admin", "tenantAdmin"]:
            raise HTTPException(403, "You do not have permission to create shifts")

        for shift in payload:
            tenant = db.query(models.tenant).filter(
                models.tenant.tenant_name.ilike(shift.tenant_name)
            ).first()

            if not tenant:
                raise HTTPException(404, f"Tenant '{shift.tenant_name}' not found")

            if role.role != "superAdmin" and current_user.tenant_id != tenant.id:
                raise HTTPException(403, detail=f"You are not authorized to create shifts for this tenant {tenant.tenant_name}")

            if not shift.timings:
                raise HTTPException(400, "Shift timings must be provided")

            exists = db.query(models.tenant_shift).filter_by(
                tenant_id=tenant.id, shift_name=shift.shift_name
            ).first()
            if exists:
                raise HTTPException(409, f"Shift '{shift.shift_name}' already exists for tenant '{tenant.tenant_name}'")

            # 🚫 Validate no duplicate weekdays in timings
            weekdays = [t.weekday for t in shift.timings]
            if len(weekdays) != len(set(weekdays)):
                raise HTTPException(400, f"Duplicate weekday found in shift '{shift.shift_name}'")

            # ✅ Check internal overlaps
            shifts_fn.check_overlap(shift.timings)

            # 🕒 Calculate total shift hours by weekday
            new_hours = {}
            for t in shift.timings:
                dur = shifts_fn.calculate_duration(t.shift_start, t.shift_end)
                new_hours[t.weekday] = new_hours.get(t.weekday, 0) + dur

            # 🔎 Get existing shift durations from DB
            existing_hours = {}
            existing_timings = (
                db.query(models.ShiftTiming)
                .join(models.tenant_shift, models.tenant_shift.id == models.ShiftTiming.tenant_shift_id)
                .filter(models.tenant_shift.tenant_id == tenant.id)
                .all()
            )
            for s in existing_timings:
                dur = shifts_fn.calculate_duration(s.shift_start, s.shift_end)
                existing_hours[s.weekday] = existing_hours.get(s.weekday, 0) + dur

            for weekday, hours in new_hours.items():
                total = existing_hours.get(weekday, 0) + hours
                if total > 24:
                    raise HTTPException(
                        400,
                        f"Total shift duration exceeds 24 hours on weekday {weekday} for tenant '{tenant.tenant_name}'"
                    )

            new_shift = models.tenant_shift(
                tenant_id=tenant.id,
                shift_name=shift.shift_name,
                created_by=current_user.id,
                updated_by=current_user.id
            )
            db.add(new_shift)
            db.flush()

            for t in shift.timings:
                db.add(models.ShiftTiming(
                    tenant_shift_id=new_shift.id,
                    shift_start=t.shift_start,
                    shift_end=t.shift_end,
                    weekday=t.weekday,
                    created_by=current_user.id,
                    updated_by=current_user.id
                ))

        db.commit()
        return {"message": "All shifts inserted successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to insert shifts: {e}")



# @router.post("/bulk", status_code=status.HTTP_201_CREATED)
# def create_multiple_shifts(
#     payload: List[schemas.TenantShiftCreate],
#     db: Session = Depends(get_db),
#     current_user: models.user = Depends(oauth2.get_current_user)
# ):
#     try:    
#         role = db.query(models.role).filter(models.role.id == current_user.role_id).first()

#         if role.role not in ["superAdmin", "admin", "tenantAdmin"]:
#             raise HTTPException(403, "You do not have permission to create shifts")

#         for shift in payload:
#             tenant = db.query(models.tenant).filter(
#                 models.tenant.tenant_name.ilike(shift.tenant_name)
#             ).first()

#             if not tenant:
#                 raise HTTPException(404, f"Tenant '{shift.tenant_name}' not found")

#             if current_user.tenant_id != role.id:
#                 raise HTTPException(403, "You are not authorized to create shifts for this tenant")

#             if not shift.timings:
#                 raise HTTPException(400, "Shift timings must be provided")

#             exists = db.query(models.tenant_shift).filter_by(
#                 tenant_id=tenant.id, shift_name=shift.shift_name
#             ).first()
#             if exists:
#                 raise HTTPException(409, f"Shift '{shift.shift_name}' already exists for tenant '{tenant.tenant_name}'")

#             shifts_fn.check_overlap(shift.timings)

#             # Validate total shift hours per weekday
#             new_hours = {}
#             for t in shift.timings:
#                 dur = shifts_fn.calculate_duration(t.shift_start, t.shift_end)
#                 new_hours[t.weekday] = new_hours.get(t.weekday, 0) + dur

#             existing_hours = {}
#             existing_timings = (
#                 db.query(models.ShiftTiming)
#                 .join(models.tenant_shift, models.tenant_shift.id == models.ShiftTiming.tenant_shift_id)
#                 .filter(models.tenant_shift.tenant_id == tenant.id)
#                 .all()
#             )
#             for s in existing_timings:
#                 dur = shifts_fn.calculate_duration(s.shift_start, s.shift_end)
#                 existing_hours[s.weekday] = existing_hours.get(s.weekday, 0) + dur

#             for weekday, hours in new_hours.items():
#                 total = existing_hours.get(weekday, 0) + hours
#                 if total > 24:
#                     raise HTTPException(
#                         400,
#                         f"Total shift duration exceeds 24 hours on weekday {weekday} for tenant '{tenant.tenant_name}'"
#                     )

#             new_shift = models.tenant_shift(
#                 tenant_id=tenant.id,
#                 shift_name=shift.shift_name,
#                 created_by=current_user.id,
#                 updated_by=current_user.id
#             )
#             db.add(new_shift)
#             db.flush()

#             for t in shift.timings:
#                 db.add(models.ShiftTiming(
#                     tenant_shift_id=new_shift.id,
#                     shift_start=t.shift_start,
#                     shift_end=t.shift_end,
#                     weekday=t.weekday,
#                     created_by=current_user.id,
#                     updated_by=current_user.id
#                 ))

#         db.commit()
#         return {"message": "All shifts inserted successfully"}
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="Failed to insert shifts {e}")
