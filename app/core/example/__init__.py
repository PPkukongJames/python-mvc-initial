"""Initial Example API"""

from fastapi import APIRouter

from app.util.log_util import setup_logger
from app.core.example.domain import ExampleDomain

from .example_controller import ExampleController

router = APIRouter()
logger = setup_logger("example")
CONTROLER = ExampleController()


@router.get("/example")
def get_example():
    """Test get method"""
    logger.info("check")
    return CONTROLER.get_process()


@router.post("/example")
def post_example(criteria: ExampleDomain):
    """Test post method"""
    logger.info("check")
    return CONTROLER.post_process(criteria)
