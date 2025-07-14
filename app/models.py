
from enum import unique    # added 
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey , Float, BigInteger,Sequence, Date, Time, UniqueConstraint #added 
from sqlalchemy.sql.sqltypes import TIMESTAMP # added 
from sqlalchemy.orm import relationship # added 
from sqlalchemy.sql.expression import text  #added 
from .database import Base #added
from msilib import sequence #added
from sqlalchemy.dialects.postgresql import JSONB

# Role table 

# Role table "super admin", "admin", "tanent_admin","user"

from sqlalchemy.orm import relationship

class role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, nullable=False)
    role = Column(String, nullable=False, unique=True)  # Add unique
    created_by = Column(Integer) # need to be get from the login user
    updated_by = Column(Integer) # need to be get from the login user
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    users = relationship("user", back_populates="role")

class tenant(Base):
    __tablename__ = "tenant"
    id = Column(BigInteger, primary_key=True, nullable=False) # assign automaically 
    tenant_name = Column(String, nullable=False,unique=True) # need to be provided by the super user
    name = Column(String, nullable=False)  # need to be provided by the super user
    email = Column(String, nullable=False, unique=True)
    is_verified_tenant = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True) # need to be provided by the super user
    contact_no = Column(String, nullable=False) # need to be provided by the super user
    address = Column(String, nullable=False) # need to be provided by the super user
    created_by = Column(Integer) # need to be get from the login user
    updated_by = Column(Integer) # need to be get from the login user
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    users = relationship("user", back_populates="tenant")



class user(Base):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, nullable=False)
    tenant_id = Column(BigInteger, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    employee_id = Column(String, nullable=False)
    is_verified_user = Column(Boolean, nullable=False, default=False)
    role_id = Column(Integer, ForeignKey("role.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    role = relationship("role", back_populates="users")
    tenant = relationship("tenant", back_populates="users")

    __table_args__ = (
        UniqueConstraint("tenant_id", "employee_id", name="uix_tenant_employee"),
    )

class tenant_shift(Base):
    __tablename__ = "tenant_shift"

    id = Column(BigInteger, primary_key=True, nullable=False)
    tenant_id = Column(BigInteger, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
    shift_name = Column(String(100), nullable=False)  # Add length limit for safety
    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    __table_args__ = (
        UniqueConstraint("tenant_id", "shift_name", name="uix_tenant_shift_name"),
    )

    timings = relationship("ShiftTiming", backref="tenant_shift", cascade="all, delete-orphan")



class ShiftTiming(Base):
    __tablename__ = "shift_timing"

    id = Column(BigInteger, primary_key=True, index=True)
    tenant_shift_id = Column(BigInteger, ForeignKey("tenant_shift.id", ondelete="CASCADE"), nullable=False)
    shift_start = Column(Time, nullable=False)
    shift_end = Column(Time, nullable=False)
    weekday = Column(Integer, nullable=False)  # 1=Mon, ..., 7=Sun

    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    __table_args__ = (
        UniqueConstraint("tenant_shift_id", "weekday", name="uix_shift_weekday"),  # Prevent duplicates
    )


# Product_operation

class Operation_List(Base):
    __tablename__ = "operation_list"

    id = Column(BigInteger, primary_key=True, nullable=False)
    tenant_id = Column(BigInteger, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
    operation_name = Column(String(100), nullable=False)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    __table_args__ = (
        UniqueConstraint("tenant_id", "operation_name", name="uix_tenant_operation_name"),
    )


class Product_Master(Base):
    __tablename__ = "product_master"
    id = Column(BigInteger, primary_key=True, nullable=False)
    tenant_id = Column(BigInteger, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String)
    product_no = Column(String)
    drawing_no = Column(String)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    operations = relationship("Operation_List", secondary="product_operation_link", backref="products")

# class Product_Master(Base):
#     __tablename__ = "product_master"
#     id = Column(BigInteger, primary_key=True, nullable=False)
#     tenant_id = Column(BigInteger, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
#     product_name = Column(String)
#     product_no = Column(String)
#     drawing_no = Column(String)
#     operation = Column(Integer, ForeignKey("operation_list.id", ondelete="CASCADE"), nullable=False)
#     created_by = Column(Integer)
#     updated_by = Column(Integer)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
#     updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class ProductOperationLink(Base):
    __tablename__ = "product_operation_link"
    id = Column(BigInteger, primary_key=True, nullable=False)
    product_id = Column(BigInteger, ForeignKey("product_master.id", ondelete="CASCADE"), nullable=False)
    operation_id = Column(BigInteger, ForeignKey("operation_list.id", ondelete="CASCADE"), nullable=False)
    sequence_no = Column(Integer, nullable=True)  # optional, for ordering operations
    __table_args__ = (
        UniqueConstraint("product_id", "operation_id", name="uix_product_operation"),
    )
    



# Mold table

class Mold_Master(Base):
    __tablename__ = "mold_master"

    id = Column(BigInteger, primary_key=True, nullable=False)
    tenant_id = Column(BigInteger, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
    mold_name = Column(String(100), nullable=False)
    mold_no = Column(String(100), nullable=False)
    type_of_mold = Column(String(100), nullable=False)
    shot_wt = Column(Float, nullable=True)
    spl_instructions = Column(JSONB, nullable=True)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    __table_args__ = (
        UniqueConstraint("tenant_id", "mold_no", name="uix_mold_no"),
    )


# Machine Master

class Machine_Master(Base):
    __tablename__ = "machine_master"

    id = Column(BigInteger, primary_key=True, nullable=False)
    tenant_id = Column(BigInteger, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)

    machine_name = Column(String(100), nullable=False)
    machine_maker = Column(String(100), nullable=False)
    machine_tonnage = Column(String(100), nullable=False)
    machine_no = Column(String(100), nullable=False)
    specification = Column(JSONB, nullable=True)

    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    __table_args__ = (
        UniqueConstraint("tenant_id", "machine_no", name="uix_machine_no"),
    )


  
class MoldMachineLink(Base):
    __tablename__ = "mold_machine_link"

    id = Column(BigInteger, primary_key=True, nullable=False)
    tenant_id = Column(BigInteger, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False)
    mold_id = Column(BigInteger, ForeignKey("mold_master.id", ondelete="CASCADE"), nullable=False)
    machine_id = Column(BigInteger, ForeignKey("machine_master.id", ondelete="CASCADE"), nullable=False)
    cycle_time = Column(Float, nullable=False)  # e.g., in seconds

    __table_args__ = (
        UniqueConstraint("tenant_id", "mold_id", "machine_id", name="uix_tenant_mold_machine"),
    )



