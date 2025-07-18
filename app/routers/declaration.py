from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import pandas as pd

from app import models, schemas, oauth2
from ..database import get_db
from ..function import fetch_details, declare  # Adjust import if needed

router = APIRouter(prefix="/ops/v1", tags=["operation"])


# def remove_duplicates(operation_list):
#     """Normalize and remove duplicates from list of operations"""
#     df_operation = pd.DataFrame(operation_list, columns=['operations'])
#     df_operation['operations'] = df_operation['operations'].str.strip().str.lower()
#     return df_operation.drop_duplicates(subset='operations', keep='first')


@router.post("/operation", status_code=status.HTTP_201_CREATED)
def create_operations(
    operation_data: schemas.TenantOperation,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user)
):
    try:
        # <---------- 1. Validate user, tenant, role ---------->
        user, tenant, role = fetch_details.user_details(current_user, db)

        if role.role.lower() != 'tenantadmin' and role.id != 3:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You don't have Admin Rights to create operation!!!"
            )

        if user.tenant_id != operation_data.tenantid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The Tenant you want to create Operation is different than yours!!!"
            )

        # <---------- 2. Remove duplicates from input ---------->
        unique_operations = declare.remove_duplicates(operation_data.operation)

        # <---------- 3. Fetch existing operations from DB ---------->
        existing_ops = db.query(models.Operation_List).filter(
            models.Operation_List.tenant_id == user.tenant_id
        ).all()
        existing_ops_set = set(op.operation_name.lower() for op in existing_ops)

        # <---------- 4. Filter only new operations ---------->
        df_unique = unique_operations[
            ~unique_operations['operations'].isin(existing_ops_set)
        ].copy()  # copy to avoid SettingWithCopyWarning

        if df_unique.empty:
            raise HTTPException(status_code=400, detail="No new operations to add")

        # <---------- 5. Add metadata columns ---------->
        
        df_unique['tenant_id'] = tenant.id
        df_unique['created_by'] = current_user.id
        df_unique['updated_by'] = current_user.id
        # df_unique['created_at'] = now # Auto feed by DB server 
        # df_unique['updated_at'] = now # Auto feed by DB server 
        df_unique.rename(columns={'operations': 'operation_name'}, inplace=True)
        print(f'*************{df_unique}')
        # <---------- 6. Bulk Insert to DB ---------->
        db.bulk_insert_mappings(
            models.Operation_List,
            df_unique.to_dict(orient='records')
        )
        db.commit()

        return {"status": "success", "inserted_operations": df_unique['operation_name'].tolist()}

    except HTTPException as he:
        raise he

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


