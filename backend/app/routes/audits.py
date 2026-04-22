from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..auth import get_current_user, require_admin
from ..db import db_cursor
from ..models import AUDIT_GRADES, AUDIT_STATUSES, RISK_LEVELS
from ..schemas import AuditCreate, AuditRead, AuditUpdate, FilterOptionsResponse, SummaryResponse


router = APIRouter(prefix="/audits", tags=["audits"])


def _map_audit(row) -> AuditRead:
    return AuditRead(
        id=row["id"],
        title=row["title"],
        department=row["department"],
        observation=row["observation"],
        risk=row["risk"],
        grade=row["grade"],
        action=row["action"],
        owner=row["owner"],
        due_date=row["due_date"],
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _build_filters(status_value: str | None, risk: str | None, department: str | None, owner: str | None):
    filters: list[str] = []
    values: list[str] = []
    if status_value:
        filters.append("status = ?")
        values.append(status_value)
    if risk:
        filters.append("risk = ?")
        values.append(risk)
    if department:
        filters.append("department = ?")
        values.append(department)
    if owner:
        filters.append("owner = ?")
        values.append(owner)

    clause = ""
    if filters:
        clause = "WHERE " + " AND ".join(filters)
    return clause, values


@router.get("", response_model=list[AuditRead])
def list_audits(
    status_value: str | None = Query(default=None, alias="status"),
    risk: str | None = Query(default=None),
    department: str | None = Query(default=None),
    owner: str | None = Query(default=None),
    current_user=Depends(get_current_user),
) -> list[AuditRead]:
    where_clause, values = _build_filters(status_value, risk, department, owner)
    query = f"""
        SELECT id, title, department, observation, risk, grade, action, owner, due_date, status, created_at, updated_at
        FROM audits
        {where_clause}
        ORDER BY due_date ASC, id DESC
    """
    with db_cursor() as (_, cursor):
        rows = cursor.execute(query, values).fetchall()
    return [_map_audit(row) for row in rows]


@router.get("/summary", response_model=SummaryResponse)
def get_summary(current_user=Depends(get_current_user)) -> SummaryResponse:
    with db_cursor() as (_, cursor):
        total = cursor.execute("SELECT COUNT(*) AS count FROM audits").fetchone()["count"]
        open_count = cursor.execute("SELECT COUNT(*) AS count FROM audits WHERE status = 'Open'").fetchone()["count"]
        closed_count = cursor.execute("SELECT COUNT(*) AS count FROM audits WHERE status = 'Closed'").fetchone()["count"]
        overdue_count = cursor.execute(
            "SELECT COUNT(*) AS count FROM audits WHERE status = 'Open' AND due_date < ?",
            (date.today().isoformat(),),
        ).fetchone()["count"]
    return SummaryResponse(total=total, open=open_count, closed=closed_count, overdue=overdue_count)


@router.get("/filters", response_model=FilterOptionsResponse)
def get_filter_options(current_user=Depends(get_current_user)) -> FilterOptionsResponse:
    with db_cursor() as (_, cursor):
        departments = [
            row["department"]
            for row in cursor.execute(
                "SELECT DISTINCT department FROM audits WHERE department != '' ORDER BY department ASC"
            ).fetchall()
        ]
        owners = [
            row["owner"]
            for row in cursor.execute(
                "SELECT DISTINCT owner FROM audits WHERE owner != '' ORDER BY owner ASC"
            ).fetchall()
        ]
    return FilterOptionsResponse(
        departments=departments,
        owners=owners,
        risks=RISK_LEVELS,
        statuses=AUDIT_STATUSES,
        grades=AUDIT_GRADES,
    )


@router.post("", response_model=AuditRead, status_code=status.HTTP_201_CREATED)
def create_audit(payload: AuditCreate, current_user=Depends(require_admin)) -> AuditRead:
    with db_cursor() as (_, cursor):
        cursor.execute(
            """
            INSERT INTO audits (
                title, department, observation, risk, grade, action, owner, due_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.title,
                payload.department,
                payload.observation,
                payload.risk.value,
                payload.grade.value,
                payload.action,
                payload.owner,
                payload.due_date.isoformat(),
                payload.status.value,
            ),
        )
        audit_id = cursor.lastrowid
        row = cursor.execute(
            """
            SELECT id, title, department, observation, risk, grade, action, owner, due_date, status, created_at, updated_at
            FROM audits WHERE id = ?
            """,
            (audit_id,),
        ).fetchone()
    return _map_audit(row)


@router.put("/{audit_id}", response_model=AuditRead)
def update_audit(audit_id: int, payload: AuditUpdate, current_user=Depends(require_admin)) -> AuditRead:
    with db_cursor() as (_, cursor):
        existing = cursor.execute("SELECT id FROM audits WHERE id = ?", (audit_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit not found")
        cursor.execute(
            """
            UPDATE audits
            SET title = ?, department = ?, observation = ?, risk = ?, grade = ?, action = ?, owner = ?, due_date = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                payload.title,
                payload.department,
                payload.observation,
                payload.risk.value,
                payload.grade.value,
                payload.action,
                payload.owner,
                payload.due_date.isoformat(),
                payload.status.value,
                audit_id,
            ),
        )
        row = cursor.execute(
            """
            SELECT id, title, department, observation, risk, grade, action, owner, due_date, status, created_at, updated_at
            FROM audits WHERE id = ?
            """,
            (audit_id,),
        ).fetchone()
    return _map_audit(row)


@router.delete("/{audit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_audit(audit_id: int, current_user=Depends(require_admin)) -> None:
    with db_cursor() as (_, cursor):
        existing = cursor.execute("SELECT id FROM audits WHERE id = ?", (audit_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit not found")
        cursor.execute("DELETE FROM audits WHERE id = ?", (audit_id,))
