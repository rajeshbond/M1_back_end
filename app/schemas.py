
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
    role: str
class RoleOut(BaseModel):
    id: int
    role: str

    class Config:
         from_attributes  = True

class tenant(BaseModel):
    tenant_name: str
    name: str
    email: EmailStr
    contact_no: str
    address: str
    class Config:
        from_attributes  = True
class tenantout(BaseModel):
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
    name: str
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

class UserCreate(BaseModel):
    email: EmailStr           # Check for proper email syntex 
    password : str
    name:  str
    phone: str
    date: date
    
    

    class Config:
        from_attributes  = True  # original 
 
class UserOut(BaseModel):  # Select BaseMolel is we select UserCreate then password field also get inhertited by default 
    id: int
    email: EmailStr
    name: str
    phone: str
    date: date
    created_at: datetime

    
    class Config:
        from_attributes  = True  
    
class ForgetPassword(BaseModel):
    email: EmailStr
    
    class Config:
        from_attributes  = True
        
class UserLogin(BaseModel):
    email: EmailStr
    password: str
   
    class Config:
        from_attributes  = True  
class UserChangePassword(BaseModel):
    password: str
    password_new: str
    
class ForgotPasswordChange(BaseModel):
    reset_code1: str
    password: str
    
class UserForgetlink(BaseModel):
    email: str
    class Config:
        from_attributes  = True 
class UserForgetPasswordOut(BaseModel):
    id: int
    class Config:
        from_attributes  = True 
 
 
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
           
class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut  
    class Config:
        from_attributes  = True

class PostOut(BaseModel):
    Post : Post
    votes : int
    class Config:
        from_attributes  = True

    

#  auth.py Token schemas
 

    
# Schemes for voting 

class Vote(BaseModel):
    post_id : int
    dir: conint(le=1) # type: ignore
class WatchListIn(BaseModel):
    symbol: str
class WatchListOut(BaseModel):
    symbol:str
    name_of_the_company:str
class ForgotPassword(BaseModel):
    email: EmailStr
class WatchiLstInCompany(BaseModel):
    name_of_the_company:str
  
    


   
    