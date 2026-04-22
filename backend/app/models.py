from enum import Enum


class RiskLevel(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class AuditGrade(str, Enum):
    a = "A"
    b = "B"
    c = "C"
    d = "D"


class AuditStatus(str, Enum):
    open = "Open"
    closed = "Closed"


RISK_LEVELS = [level.value for level in RiskLevel]
AUDIT_GRADES = [grade.value for grade in AuditGrade]
AUDIT_STATUSES = [status.value for status in AuditStatus]
