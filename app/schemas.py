
from datetime import datetime , date, time
from operator import le
from pydantic import BaseModel, EmailStr, Field , conint
from typing import List, Optional
from app.models import *
from pydantic.types import conlist

class ShiftName(BaseModel):
    shift_name: str
    tenant_name:str

class RoleCreate(BaseModel):
    user_role: str
class RoleOut(BaseModel):
    id: int
    user_role: str

    class Config:
         from_attributes  = True

class Tenant(BaseModel):
    tenant_name: str
    name: str
    email: EmailStr
    contact_no: str
    address: str
    class Config:
        from_attributes  = True
class Tenantout(BaseModel):
    id: int
    tenant_name: str
    name: str
    email: EmailStr
    contact_no: str
    address: str
    created_at: datetime    

    class Config:
        from_attributes  = True
class TUser(BaseModel):
    name: str
    tname: str
    employee_id: str
    email: EmailStr
    role: str
    password: str
    phone: str
    
    class Config:
        from_attributes  = True

class TUserOut(BaseModel):
    name: str
    tname: str
    employee_id: str
    email: EmailStr
    role: str
    phone: str
    created_at: datetime
    
    class Config:
        from_attributes  = True

class UserResponse(BaseModel):
    id: int
    user_name: str
    email: EmailStr
    employee_id: str
    phone: Optional[str]
    tenant_id: int
    role_id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    

class TokenData(BaseModel):
    id: Optional[str] = None



class ShiftTimingCreate(BaseModel):
    shift_start: time = Field(..., example="08:00")
    shift_end: time = Field(..., example="16:00")
    weekday: int = Field(..., ge=1, le=7, example=1) # 1 = Monday to 7 = Sunday

class TenantShiftCreate(BaseModel):
    tenant_name: str
    shift_name: str
    timings: List[ShiftTimingCreate]    

class TenantOperation(BaseModel):
    tenantid: int
    operation: List[str] # or List[YourOperationModel] if you have a nested schema
# -------------------------------------------------------------------------------------------
# Old schema for refernace only 
