from fastapi import APIRouter
from app.util.log_util import setup_logger
from .example_controller import ExampleController
from .domain import ExampleDomain

router = APIRouter()
logger = setup_logger('example')
CONTROLER = ExampleController()
@router.get("/example")
def get_example():
    logger.info('check')
    return CONTROLER.get_process()

@router.post("/example")
def post_example(criteria:ExampleDomain):
    logger.info('check')
    return CONTROLER.post_process(criteria)

