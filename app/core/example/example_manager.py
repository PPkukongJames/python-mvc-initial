"""Example Manager"""

from typing import List
from fastapi import File, UploadFile

from app.core.example.domain import ExampleSubmitUploadDomain
from app.util.log_util import set_application_log

from .example_service import ExampleService

LOGGER = set_application_log(__name__)


class ExampleManager:
    """Manager Example class"""

    logger = None
    manager = None

    def __init__(self):
        self.logger = LOGGER
        self.service = ExampleService()

    def process(self):
        """process example"""
        return self.service.process()

    async def upload_files(self,files: List[UploadFile] = File(...)):
        """upload file manager"""
        response = {}
        self.logger.debug("send to validate")
        if await self.service.validate_files(files) :
            self.logger.debug("create tmp file")
            response = await self.service.create_tmp_file(files)
        return {
            "result":response
        }

    def submit_files_upload(self,criteria:ExampleSubmitUploadDomain):
        """Create original file after submit"""
        return {
            "response": self.service.submit_files_upload(criteria)
        }
