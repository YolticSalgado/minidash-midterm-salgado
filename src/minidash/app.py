"""Application factory. Run with: uvicorn --factory minidash.app:create_app --app-dir src"""

import asyncio
import os
from contextlib import asynccontextmanager, closing

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from minidash import services
from minidash.clock import Clock, SystemClock
from minidash.db import connect, init_db
from minidash.errors import DomainError
from minidash.routes import router
from minidash.worker import run_release_loop


def create_app(
    db_path: str | None = None,
    clock: Clock | None = None,
    release_interval_seconds: float = 30.0,
) -> FastAPI:
    db_path = db_path or os.environ.get("MINIDASH_DB", "minidash.db")
    clock = clock or SystemClock()
    init_db(db_path)

    def release_once() -> list[int]:
        with closing(connect(db_path)) as conn:
            return services.release_due_orders(conn, clock.now())

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Catch up on anything that came due while the app was down, before serving requests.
        await asyncio.to_thread(release_once)
        stop = asyncio.Event()
        task = asyncio.create_task(run_release_loop(release_once, release_interval_seconds, stop))
        yield
        stop.set()
        await task

    app = FastAPI(title="MiniDash", lifespan=lifespan)
    app.state.db_path = db_path
    app.state.clock = clock
    app.include_router(router)

    @app.exception_handler(DomainError)
    def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    return app
