from fastapi import APIRouter
from app.util.log_util import setup_logger

logger = setup_logger('example')
router = APIRouter()

@router.get("/example")
def get_example():
    logger.info('check')
    return {"message": "This is an example response."}
