from fastapi import FastAPI,Request
from app.util.log_util import setup_logger,set_submit_id
import uvicorn 
import json
import contextvars
import random
import string
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
    body_str = None
    try :
        body_str = dict(json.loads(body.decode("utf-8")))# แปลงเป็น string
    except :  # noqa: E722
        None
    #ตั้งค่า submitId ใน ContextVar
    submit_id = None
    if 'submitId' in list(request.query_params.keys()) :
        submit_id = request.query_params['submitId']
    else :
        submit_id = generate_random_string()
        
    set_submit_id("-submitId-"+submit_id+"-path-"+request.url.path)
    
    logger.debug(f"New request: {request.method} {request.url}")
    logger.debug(f"body : {body_str}")

    response = await call_next(request)
    
    return response

def generate_random_string(length=5):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

app.include_router(example_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)