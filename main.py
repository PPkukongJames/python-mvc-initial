"""Main file"""

import logging
import contextvars
import json
from contextlib import asynccontextmanager  # noqa: E402

import uvicorn
from fastapi import FastAPI, Request
from starlette.responses import Response

from middleware_filter import get_client_ip, get_endpoint, get_name, get_submit_id

from app.core.config.application import APPLICATION_CONFIG
from app.core.example import router as example_router
from app.util.log_util import (  # Import log_util จาก app.util
    set_add_on_thread,
    set_application_log,
    setup_entry_exit,
    init_log,
    write_access_log,
)

# entry_exit = setup_entry_exit('main-kafka')
app = FastAPI()
access_logger = logging.getLogger("api.access")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Middleware"""
    logger.info("Application startup")
    yield
    # Shutdown
    logger.info("Application shutdown")


logger = set_application_log(__name__)
entry_exit = setup_entry_exit()
app = FastAPI(lifespan=lifespan)

submit_id_var = contextvars.ContextVar("submit_id", default="")


@app.middleware("http")
async def log_request(request: Request, call_next):
    # ดึงค่าจาก body
    """Request"""
    # ดึงค่าจาก body
    body = await request.body()
    body_str = dict(json.loads(body.decode("utf-8")))  # แปลงเป็น string
    fullname = await get_name(request)
    client_ip = get_client_ip(request)
    submit_id = get_submit_id(request)
    path = get_endpoint(request)

    # ตั้งค่า submitId ใน ContextVar
    set_add_on_thread(f"-submitId-{submit_id}-path-{request.method} {path}")

    entry_exit.info(", %s,%s,%s,%s,%s,,", "ENTRY", submit_id, fullname, client_ip, path)

    logger.debug("New request: %s %s %s", request.method, request.url, fullname)
    logger.debug("body %s", body_str)

    response = await call_next(request)
    write_access_log(request, response)
    error = ""
    if response.status_code != 200:
        response_body = b"".join([chunk async for chunk in response.body_iterator])
        response = Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

        error = "error:" + str(dict(json.loads(response_body.decode("utf-8")))).replace(
            ",", ""
        ).replace("'", "")

    entry_exit.info(
        ", %s,%s,%s,%s,%s,%s,", "EXIT", submit_id, fullname, client_ip, path, error
    )

    return response


app.include_router(example_router, prefix="/api")


if __name__ == "__main__":
    log_config_dict = init_log()
    if APPLICATION_CONFIG["environment"] == "local":  # enable auto-reload after save
        uvicorn.run(
            "main:app",
            host=APPLICATION_CONFIG["host"],
            port=APPLICATION_CONFIG["port"],
            workers=1,
            log_level="info",
            reload=True,
            log_config=log_config_dict,
        )
    else:
        uvicorn.run(
            app,
            host=APPLICATION_CONFIG["host"],
            port=APPLICATION_CONFIG["port"],
            log_config=log_config_dict,
        )
