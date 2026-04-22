from datetime import date, timedelta

from .models import AuditGrade, AuditStatus, RiskLevel


SAMPLE_AUDITS = [
    {
        "title": "Late vendor reconciliations",
        "department": "Finance",
        "observation": "Monthly vendor reconciliation files were completed after the control deadline.",
        "risk": RiskLevel.high.value,
        "grade": AuditGrade.c.value,
        "action": "Automate reconciliation reminders and introduce review sign-off.",
        "owner": "Ahmed Ali",
        "due_date": (date.today() + timedelta(days=10)).isoformat(),
        "status": AuditStatus.open.value,
    },
    {
        "title": "Missing access review evidence",
        "department": "IT",
        "observation": "Quarterly privileged access review evidence was not attached for two systems.",
        "risk": RiskLevel.critical.value,
        "grade": AuditGrade.d.value,
        "action": "Collect review evidence and add approval archive process.",
        "owner": "Sara Hassan",
        "due_date": (date.today() - timedelta(days=4)).isoformat(),
        "status": AuditStatus.open.value,
    },
    {
        "title": "Warehouse checklist gap",
        "department": "Operations",
        "observation": "Daily warehouse safety checklist was updated but not consistently signed.",
        "risk": RiskLevel.medium.value,
        "grade": AuditGrade.b.value,
        "action": "Move checklist to digital form with mandatory supervisor confirmation.",
        "owner": "Mona Khaled",
        "due_date": (date.today() + timedelta(days=21)).isoformat(),
        "status": AuditStatus.closed.value,
    },
]
