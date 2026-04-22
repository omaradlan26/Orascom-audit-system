from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import bootstrap_admin_user
from .db import initialize_database, seed_audits_if_empty
from .routes.auth import router as auth_router
from .routes.audits import router as audits_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    bootstrap_admin_user()
    seed_audits_if_empty()
    yield


app = FastAPI(
    title="Orascom Audit Management API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(audits_router)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
