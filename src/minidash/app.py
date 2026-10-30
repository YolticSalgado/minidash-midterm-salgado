"""Application factory. Run with: uvicorn --factory minidash.app:create_app --app-dir src"""

import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from minidash.db import init_db
from minidash.errors import DomainError
from minidash.routes import router


def create_app(db_path: str | None = None) -> FastAPI:
    db_path = db_path or os.environ.get("MINIDASH_DB", "minidash.db")
    init_db(db_path)

    app = FastAPI(title="MiniDash")
    app.state.db_path = db_path
    app.include_router(router)

    @app.exception_handler(DomainError)
    def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    return app
