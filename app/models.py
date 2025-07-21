from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey, Float, BigInteger,
    Sequence, Date, Time, UniqueConstraint, Index
)
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from .database import Base
from sqlalchemy.dialects.postgresql import JSONB

# <-------------------------- Role Table starts
class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True, nullable=False)
    user_role = Column(String, nullable=False, unique=True)
    created_by = Column(BigInteger)
    updated_by = Column(BigInteger)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # Relationship
    users = relationship("User", back_populates="role")
# ---------------------------> Role table ends


# <-------------------------- Tenant table starts
class Tenant(Base):
    __tablename__ = 'tenant'

    id = Column(BigInteger, primary_key=True, nullable=False)
    tenant_name = Column(String, nullable=False, unique=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(BigInteger)
    updated_by = Column(BigInteger)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # Relationship
    users = relationship("User", back_populates="tenant")
# ---------------------------> Tenant table ends


# <-------------------------- User table starts
class User(Base):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True, nullable=False)
    tenant_id = Column(BigInteger, ForeignKey('tenant.id', ondelete='CASCADE'), nullable=False)
    role_id = Column(Integer, ForeignKey('role.id', ondelete="CASCADE"), nullable=False)
    employee_id = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    password = Column(String,nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(BigInteger)
    updated_by = Column(BigInteger)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # Relationships
    role = relationship("Role", back_populates="users")
    tenant = relationship("Tenant", back_populates="users")

    __table_args__ = (
        UniqueConstraint('tenant_id', 'employee_id', name='uix_tenant_employee'),
    )
# ---------------------------> User table ends
