from sqlalchemy.orm import Session
from app import oauth2, schemas
from ..database import get_db
from .. import models,utls
from fastapi import Response, status, HTTPException, Depends, APIRouter
import pandas as pd
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

router = APIRouter(
    prefix= "/admin",
    tags=["Admin"]
)

# post Role Api 

@router.post("/role", status_code=status.HTTP_201_CREATED, response_model=schemas.RoleOut)
def appRole(
    role: schemas.RoleCreate,
    db: Session = Depends(get_db),
    current_user: models.user = Depends(oauth2.get_current_user)
):
    try:
        # 🚫 Remove debug print statements in production
        if current_user.role_id > 2:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"{current_user.name}, you don't have privilege to add Role. Please contact Admin!"
            )

        role_info = db.query(models.role).filter(models.role.role == role.role).first()

        if role_info:
            # ✅ Safe to print since we know role_info is not None
            # print(role_info.role)  # ← optional debug, remove for production
            raise HTTPException(
                status_code=status.HTTP_208_ALREADY_REPORTED,
                detail=f"Role '{role.role}' already exists!"
            )

        new_role_input = {
            "role": role.role,
            "created_by": current_user.id,
            "updated_by": current_user.id
        }

        new_role = models.role(**new_role_input)
        db.add(new_role)
        db.commit()
        db.refresh(new_role)

        return new_role

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

@router.post("/tenant",
              status_code= status.HTTP_201_CREATED,
            #   response_model=schemas.tenantout
              ) 
def appTenant(
    tenant: schemas.tenant,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
    ):
   try:
        print(current_user.role_id)
        # user = db.query(models.user).filter(models.user.id == current_user.id).first()
        # if not user:
        #     raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="user not found")
        if  current_user.role_id > 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to create a tenant"
            )
        if not current_user.is_verified_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to create a tenant"
            )
        tenant_info = db.query(models.tenant).filter(
            func.lower(models.tenant.tenant_name) == tenant.tenant_name.lower()).first()
        if tenant_info:
            raise HTTPException(
                status_code=status.HTTP_208_ALREADY_REPORTED,
                detail=f"Tenant '{tenant.tenant_name}' already exists!")
        create = {"created_by":current_user.id,"updated_by":current_user.id}
        new_tenant = models.tenant(**create,**tenant.model_dump())
        db.add(new_tenant)
        db.commit()
        db.refresh(new_tenant)
        return {"new_tenant": new_tenant}
        pass
   except Exception as e:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail= f"{e}")
   

@router.post("/user", status_code=status.HTTP_201_CREATED)
def appUser(
    tuser: schemas.TUser,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
    ):

    
    try:
        if current_user.role_id > 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to create a user"
            )
        tenant = db.query(models.tenant).filter(
            func.lower(models.tenant.tenant_name) == tuser.tname.lower()
        ).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found, 1st create a tenant")
        if not tenant.is_verified_tenant:
            raise HTTPException(status_code=400, detail="Tenant is not varified, Please contact your Admin")
        
        if not tenant.is_active :
            raise HTTPException(status_code=400, detail="Tenant is not active, Please contact your")

        employee_duplicate = db.query(models.user).filter(
            func.lower(models.user.employee_id) == tuser.employee_id.lower(),models.user.tenant_id == tenant.id
        ).first()
        if employee_duplicate:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{tuser.employee_id} is already registered as user with tenant {tenant.tenant_name} with employee name {employee_duplicate.name}"
            )
        # Duplicate code ......

    
        # user_qury = db.query(models.user).filter(
        #     func.lower(models.user.employee_id) == tuser.employee_id,
        #     models.user.email == tuser.email,models.user.tenant_id == tenant.id
        # )
        # us = user_qury.first()
        # if us:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail=f"{tuser.name} is already registered as user for tenant {tenant.tenant_name}"
        #     )

        role = db.query(models.role).filter(
            func.lower(models.role.role) == tuser.role.lower()
        ).first()
        if not role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Such Role is not available")

        hashed_password = utls.hash(tuser.password)
        tuser.password = hashed_password

        new_user_data = {
            "tenant_id": tenant.id,
            "name": tuser.name,
            "email": tuser.email,
            "password": tuser.password,
            "employee_id": tuser.employee_id,
            "phone": tuser.phone,
            "role_id": role.id,
            "created_by": current_user.id,
            "updated_by": current_user.id
        }

        new_user = models.user(**new_user_data)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except HTTPException:
        raise  # Don't override intended errors

    except Exception as e:
        # Log error properly and send safe message
        print("Unexpected Error:", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
# 
# 
#  very important route don't delete
# 
#  
@router.post("/fuser", status_code=status.HTTP_201_CREATED)
def appUserfirst(
    tuser: schemas.TUser,
    db: Session = Depends(get_db),
    # current_user: int = Depends(oauth2.get_current_user)
    ):

    
    try:
        # if current_user.role_id > 2:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="You are not authorized to create a user"
        #     )
        tenant = db.query(models.tenant).filter(
            func.lower(models.tenant.tenant_name) == tuser.tname.lower()
        ).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        if not tenant.is_verified_tenant:
            raise HTTPException(status_code=400, detail="Tenant is not varified, Please contact your Admin")
        
        if not tenant.is_active :
            raise HTTPException(status_code=400, detail="Tenant is not active, Please contact your")

        user_qury = db.query(models.user).filter(
            func.lower(models.user.employee_id) == tuser.employee_id,
            models.user.email == tuser.email
        )
        us = user_qury.first()
        if us:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{tuser.name} is already registered as user for tenant {tenant.tenant_name}"
            )

        role = db.query(models.role).filter(
            func.lower(models.role.role) == tuser.role.lower()
        ).first()
        if not role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not found")

        hashed_password = utls.hash(tuser.password)
        tuser.password = hashed_password

        new_user_data = {
            "tenant_id": tenant.id,
            "name": tuser.name,
            "email": tuser.email,
            "password": tuser.password,
            "employee_id": tuser.employee_id,
            "phone": tuser.phone,
            "role_id": role.id,
            "created_by": 1,
            "updated_by": 1
        }

        new_user = models.user(**new_user_data)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"new_user": new_user}

    except HTTPException:
        raise  # Don't override intended errors

    except Exception as e:
        # Log error properly and send safe message
        print("Unexpected Error:", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

   
@router.post("/ftenant",
              status_code= status.HTTP_201_CREATED,
            #   response_model=schemas.tenantout
              ) 
def appTenant_first(
    tenant: schemas.tenant,
    db: Session = Depends(get_db),
    # current_user: int = Depends(oauth2.get_current_user)
    ):
   try:
        # print(current_user.role_id)
        # user = db.query(models.user).filter(models.user.id == current_user.id).first()
        # if not user:
        #     raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="user not found")
        # if  current_user.role_id > 2:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="You are not authorized to create a tenant"
        #     )
        # if not current_user.is_verified_user:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="You are not authorized to create a tenant"
        #     )
        # tenant_info = db.query(models.tenant).filter(
        #     func.lower(models.tenant.tenant_name) == tenant.tenant_name.lower()).first()
        # if tenant_info:
        #     raise HTTPException(
        #         status_code=status.HTTP_208_ALREADY_REPORTED,
        #         detail=f"Tenant '{tenant.tenant_name}' already exists!")
        create = {"created_by":0,"updated_by":0}
        new_tenant = models.tenant(**create,**tenant.model_dump())
        db.add(new_tenant)
        db.commit()
        db.refresh(new_tenant)
        return {"new_tenant": new_tenant}
        pass
   except Exception as e:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail= f"{e}")
