from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from .models import AuditGrade, AuditStatus, RiskLevel


RoleType = Literal["admin", "viewer"]


class AuditBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    department: str = Field(min_length=1, max_length=100)
    observation: str = Field(min_length=1)
    risk: RiskLevel
    grade: AuditGrade
    action: str = Field(min_length=1)
    owner: str = Field(min_length=1, max_length=100)
    due_date: date
    status: AuditStatus = AuditStatus.open


class AuditCreate(AuditBase):
    pass


class AuditUpdate(AuditBase):
    pass


class AuditRead(AuditBase):
    id: int
    created_at: datetime
    updated_at: datetime


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=200)


class AuthResponse(BaseModel):
    token: str
    username: str
    role: RoleType


class SummaryResponse(BaseModel):
    total: int
    open: int
    closed: int
    overdue: int


class FilterOptionsResponse(BaseModel):
    departments: list[str]
    owners: list[str]
    risks: list[str]
    statuses: list[str]
    grades: list[str]
