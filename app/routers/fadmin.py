from fastapi import APIRouter, Depends, HTTPException, status, utils
from sqlalchemy import Null
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import pandas as pd
from .. import utls

from app import models, schemas, oauth2
from ..database import get_db
from ..function import fetch_details, declare  # Adjust import if needed

router = APIRouter(prefix="/fadmin", tags=["fAdmin"])

# Create Role only for superAdmin
@router.post("/role",status_code=status.HTTP_201_CREATED)
def create_frole(db:Session = Depends(get_db)):
  try:
    # Creating Role Super Admin
    new_role = {
      "user_role": "superadmin",
      "created_by" : 1,
      "updated_by":1
    } 
    new_role = models.Role(**new_role)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    # creating tenant infomiles
    new_tenant = {
      "tenant_name":"infomiles",
      "created_by":1,
      "updated_by":1
    }
    new_tenant = models.Tenant(**new_tenant)
    db.add(new_tenant)
    db.commit()
    db.refresh(new_tenant)
    # user user creation 
    super_user = {
      "tenant_id":new_tenant.id,
      "role_id":new_role.id,
      "employee_id":"info01",
      "user_name":"Rajesh Bondgilwar",
      "email":"rajesh.bondgilwar@infomiles.in",
      "password":utls.hash("Rajesh@2024"),
      "created_by":1,
      "updated_by":1

    }
    new_user = models.User(**super_user)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message":"sucessful","role":new_role,"tenant":new_tenant,"user":new_user}
  except HTTPException as he:
    raise he  
  except SQLAlchemyError as e:
    db.rollback()
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Database error: {str(e)}")
  except Exception as e:
    db.rollback()
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Unexpected error:{str (e)} ")