"""Main file"""

import contextvars
import json
import random
import string
from contextlib import asynccontextmanager  # noqa: E402

import uvicorn
from fastapi import FastAPI, Request

from app.core.config.application import APPLICATION_CONFIG
from app.core.example import router as example_router
from app.util.log_util import set_submit_id, setup_logger

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Middleware"""
    logger.info("Application startup")
    yield
    # Shutdown
    logger.info("Application shutdown")


logger = setup_logger("main")
app = FastAPI(lifespan=lifespan)

submit_id_var = contextvars.ContextVar("submit_id", default="")


@app.middleware("http")
async def log_request(request: Request, call_next):
    """Manager request before go ahead into endpoint."""
    # ดึงค่าจาก body
    body = await request.body()
    body_str = body.decode("utf-8")
    if body_str.strip() != "" :
        body_str = dict(json.loads(body_str))  # แปลงเป็น string

    # ตั้งค่า submitId ใน ContextVar
    submit_id = None
    if "submitId" in list(request.query_params.keys()):
        submit_id = request.query_params["submitId"]
    else:
        submit_id = generate_random_string()

    set_submit_id("-submitId-" + submit_id + "-path-" + request.url.path)

    logger.debug("New request: %s %s",request.method,request.url)
    logger.debug("body : %s",body_str)

    response = await call_next(request)

    return response


def generate_random_string(length=5):
    """Generate submit id for each request"""
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


app.include_router(example_router, prefix="/api")

if __name__ == "__main__":
    if APPLICATION_CONFIG["environment"] == "local":  # enable auto-reload after save
        uvicorn.run(
            "main:app",
            host=APPLICATION_CONFIG["host"],
            port=APPLICATION_CONFIG["port"],
            workers=1,
            log_level="info",
            reload=True,
        )
    else:
        uvicorn.run(
            app, host=APPLICATION_CONFIG["host"], port=APPLICATION_CONFIG["port"]
        )
