from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd

from app import oauth2, schemas
from .. import models, utls
from ..database import get_db

router = APIRouter(
    prefix="/tenant/v1",
    tags=["Tenant"]
)

# Roles that CANNOT be created by a tenant user
RESTRICTED_ROLES = ["superAdmin", "admin", "tenantAdmin"]


@router.post("/user", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def tenantUser(
    tuser: schemas.TUser,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    try:
        # Role must be provided
        if not tuser.role:
            raise HTTPException(status_code=403, detail="Role must be provided")

        # Disallow creation of restricted roles
        if tuser.role.strip().lower() in [r.lower() for r in RESTRICTED_ROLES]:
            raise HTTPException(
                status_code=403,
                detail=f"You are not authorized to create a user with role '{tuser.role}'"
            )

        # Only users with role_id <= 3 can create other users
        if current_user.role_id > 3:
            raise HTTPException(status_code=403, detail="You are not authorized to create a user")

        # Find tenant by name
        tenant = db.query(models.tenant).filter(
            func.lower(models.tenant.tenant_name) == tuser.tname.strip().lower()
        ).first()

        if not tenant:
            raise HTTPException(status_code=404, detail=f"Tenant '{tuser.tname}' not found")

        # Ensure user creating belongs to the tenant or has super privileges
        if current_user.tenant_id != tenant.id and current_user.role_id >= 3:
            raise HTTPException(status_code=403, detail="You are not authorized to create a user for this tenant")

        if not tenant.is_verified_tenant:
            raise HTTPException(status_code=400, detail="Tenant is not verified. Please contact your Admin")

        if not tenant.is_active:
            raise HTTPException(status_code=400, detail="Tenant is not active. Please contact your Admin")

        # Check for existing user with same employee_id in this tenant
        existing_user = db.query(models.user).filter(
            func.lower(models.user.employee_id) == tuser.employee_id.strip().lower(),
            models.user.tenant_id == tenant.id
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=403,
                detail=f"User '{tuser.name}' is already registered with employee ID '{tuser.employee_id}' for tenant '{tenant.tenant_name}'"
            )

        # Find role ID from DB
        role = db.query(models.role).filter(
            func.lower(models.role.role) == tuser.role.strip().lower()
        ).first()

        if not role:
            raise HTTPException(status_code=404, detail=f"Role '{tuser.role}' not found in the system")

        # Hash the password
        hashed_password = utls.hash(tuser.password)

        # Create new user object
        new_user = models.user(
            tenant_id=tenant.id,
            name=tuser.name,
            email=tuser.email,
            password=hashed_password,
            employee_id=tuser.employee_id.strip(),
            phone=tuser.phone,
            role_id=role.id,
            created_by=current_user.id,
            updated_by=current_user.id
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except HTTPException:
        raise  # Forward expected HTTP errors

    except Exception as e:
        print("Unexpected Error:", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
