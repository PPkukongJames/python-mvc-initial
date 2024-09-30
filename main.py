from fastapi import FastAPI,Request
from app.util.log_util import setup_logger,set_submit_id  # Import log_util จาก app.util
import uvicorn 
import json
import contextvars
from contextlib import asynccontextmanager  # noqa: E402

from app.core.example import router as example_router

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application startup")
    yield
    # Shutdown
    logger.info("Application shutdown")

    
logger = setup_logger('main')
app = FastAPI(lifespan=lifespan)

submit_id_var = contextvars.ContextVar('submit_id', default='')

@app.middleware("http")
async def log_request(request: Request, call_next):
    # ดึงค่าจาก body
    body = await request.body()
    body_str = body.decode("utf-8") # แปลงเป็น string
    body_dict = json.loads(body_str)
    #ตั้งค่า submitId ใน ContextVar
    set_submit_id("-submitId-"+body_dict['submitId'])
    
    logger.debug(f"New request: {request.method} {request.url}")
    logger.debug(f"body : {body_str}")

    response = await call_next(request)
    
    return response

app.include_router(example_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)