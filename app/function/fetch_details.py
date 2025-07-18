

from app import models


def user_details(user,db):
    user = db.query(models.user).filter(models.user.id == user.id).first()
    if not user :
        return None, None, None
    tenant = db.query(models.tenant).filter(models.tenant.id==user.tenant_id).first()
    if not tenant:
        return None,None,None
    user_role = db.query(models.role).filter(models.role.id == user.role_id).first()
    if not user_role:
        return None,None,None
    
    return user, tenant, user_role

def tenant_present(tenant_name,db):
    tenant= db.query(models.tenant).filter(models.tenant.tenant_name == tenant_name).first()
    if not tenant:
        return False
    
    return tenant