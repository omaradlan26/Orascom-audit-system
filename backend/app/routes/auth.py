from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import create_session, delete_session, get_current_user, verify_password
from ..db import db_cursor
from ..schemas import AuthResponse, LoginRequest


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/guest", response_model=AuthResponse)
def login_as_guest() -> AuthResponse:
    token = create_session(username="guest", role="viewer")
    return AuthResponse(token=token, username="guest", role="viewer")


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest) -> AuthResponse:
    with db_cursor() as (_, cursor):
        user = cursor.execute(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (payload.username,),
        ).fetchone()

    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_session(username=user["username"], role=user["role"])
    return AuthResponse(token=token, username=user["username"], role=user["role"])


@router.get("/me", response_model=AuthResponse)
def get_me(current_user=Depends(get_current_user)) -> AuthResponse:
    return AuthResponse(
        token=current_user["token"],
        username=current_user["username"],
        role=current_user["role"],
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user=Depends(get_current_user)) -> None:
    delete_session(current_user["token"])
