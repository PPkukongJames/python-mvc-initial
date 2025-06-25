"""Example Service"""

from typing import List
from fastapi import File, UploadFile

from app.core.example.domain import ExampleSubmitUploadDomain
from app.util.log_util import set_application_log
from app.util.upload_file_util.domain import SubmitFilesDomain,FileUploaded
from app.util.upload_file_util import UploadFileUtil
LOGGER = set_application_log(__name__)

FILE_UTIL = UploadFileUtil()
class ExampleService:
    """Service Example class"""

    logger = None
    manager = None

    def __init__(self):
        self.logger = LOGGER

    def process(self):
        """Example method"""
        return {"message": "This is an example response."}

    async def validate_files(self,files: List[UploadFile] = File(...)):
        """upload file manager"""
        status = False
        if len(set([FILE_UTIL.validate_file_type(file) for file in files])) > 1 :
            status = False
        self.logger.debug("validate file type success")
        status = await FILE_UTIL.validate_limit_files_size(files)
        self.logger.debug("validate file limit success")
        return status

    async def create_tmp_file(self,files: List[UploadFile] = File(...)):
        """create file.tmps"""
        return await FILE_UTIL.create_list_tmp_file(files)

    def submit_files_upload(self,criteria:ExampleSubmitUploadDomain):
        """Create original file after submit"""

        files = SubmitFilesDomain()

        for data in criteria.files :
            file = FileUploaded(
                filename_original = data.filename_original,
                filename_tmp = data.filename_tmp
            )

            files.files.append(file)

        return FILE_UTIL.create_source_files(files)
