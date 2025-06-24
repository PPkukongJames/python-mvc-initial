"""Initial Example API"""

from typing import List

from fastapi import APIRouter, File, UploadFile, Form

from app.util.log_util import setup_logger
from app.core.example.domain import ExampleDomain,ExampleSubmitUploadDomain

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


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...), example: str = Form(...)):
    """Upload multi-files"""

    logger.info("user '%s' upload num of file %s", example, len(files))
    return await CONTROLER.upload_files(files)

@router.post("/submit")
def submit_files(criteria: ExampleSubmitUploadDomain):
    """submit multi-files"""

    return CONTROLER.submit_files_upload(criteria)
