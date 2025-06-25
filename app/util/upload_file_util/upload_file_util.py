"""Upload file util"""

import os
import time
import shutil
from typing import List

from fastapi import UploadFile, HTTPException

from app.util.log_util import set_application_log
from app.util.upload_file_util.domain import SubmitFilesDomain
from app.core.config.application import APPLICATION_CONFIG

LOGGER = set_application_log(__name__)

TMP_DIRECTORY = os.path.join(APPLICATION_CONFIG["tmp_directory"])
if not os.path.exists(TMP_DIRECTORY):
    os.makedirs(TMP_DIRECTORY)

SOURCE_DIRECTORY = os.path.join(APPLICATION_CONFIG["source_directory"])
if not os.path.exists(TMP_DIRECTORY):
    os.makedirs(TMP_DIRECTORY)


class UploadFileUtil:
    """Util for upload"""

    logger = None

    def __init__(self):
        self.logger = LOGGER

    def validate_file_type(self, file: UploadFile):
        """validate file type"""
        if file.content_type not in APPLICATION_CONFIG["allow_file_type"]:
            raise HTTPException(
                status_code=400,
                detail=f"Filename {file.filename} is "
                + f"file type '{file.content_type}' "
                + "is not allowed.",
            )
        return True

    async def validate_file_size(self, file: UploadFile) -> int:
        """validate limit file size each file"""
        file_content = await file.read()
        if len(file_content) > APPLICATION_CONFIG["limit_each_file_size"]:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' exceeds the maximum allowed size of "
                + f"{APPLICATION_CONFIG['limit_each_file_size'] // (1024 * 1024)} MB.",
            )

        # Reset pointer (จำเป็นหลังจากอ่านไฟล์)
        file.file.seek(0)
        self.logger.debug(
            "\nfilename %s\nfile size %s", file.filename, len(file_content)
        )
        return len(file_content)

    async def validate_limit_files_size(self, files: List[UploadFile]):
        """validate limit file size each file and total request"""
        if (
            sum([await self.validate_file_size(file) for file in files])
            > APPLICATION_CONFIG["limit_each_file_size"]
        ):
            raise HTTPException(
                status_code=400,
                detail="Total file size over limit",
            )

        return True

    async def create_tmp_file(self, file: UploadFile):
        """create .tmp file"""
        tmp_name = str(time.time_ns()) + ".tmp"
        self.logger.debug("tmp : %s", tmp_name)
        self.logger.debug("tmp location : %s", TMP_DIRECTORY + tmp_name)
        with open(TMP_DIRECTORY + tmp_name, "wb") as buffer:
            buffer.write(await file.read())

        return {"filename_tmp": tmp_name, "filename_original": file.filename}

    async def create_list_tmp_file(self, files: List[UploadFile]):
        """create tmp file from list file"""
        self.logger.debug("create_list_tmp_file")
        return [await self.create_tmp_file(file) for file in files]

    def create_source_files(
        self, files_submit: SubmitFilesDomain, path: str = "", replace: bool = False
    ):
        """Create source from file.tmp"""
        response = []
        for file in files_submit.files:
            tmp_filepath = TMP_DIRECTORY + file.filename_tmp
            if not os.path.exists(tmp_filepath):
                raise HTTPException(status_code=404, detail="File not found")

            # create folder
            path_original = SOURCE_DIRECTORY + path
            if not os.path.exists(path_original):
                os.makedirs(os.path.dirname(path_original))

            # newfile
            original_filename = path_original + file.filename_original

            # ถ้า replace is False จะ error ถ้าไฟล์ชื่อซ้ำ
            if os.path.exists(original_filename) and not replace:
                raise HTTPException(
                    status_code=409,
                    detail= f"File already exists: {original_filename}."
                            +" Set replace=True to overwrite.",
                )

            os.makedirs(os.path.dirname(original_filename), exist_ok=True)

            # read .tmp for create original file
            with (
                open(tmp_filepath, "rb") as old_file,
                open(original_filename, "wb") as new_file,
            ):
                shutil.copyfileobj(old_file, new_file)

            os.remove(tmp_filepath)

            response.append({"filename": file.filename_original, "success": True})
        return response

    def move_file(self,source: str, destination: str, replace: bool = False):
        """Move a file from `source` to `destination`."""
        # ตรวจสอบว่าไฟล์ต้นทางมีอยู่หรือไม่
        if not os.path.exists(source):
            raise HTTPException(status_code=404, detail=f"Source file not found: {source}")

        # ตรวจสอบว่าไฟล์เป้าหมายมีอยู่แล้วหรือไม่
        if os.path.exists(destination) and not replace:
            raise HTTPException(
                    status_code=409, 
                    detail= f"Destination file already exists: {destination}."
                            +" Set replace=True to overwrite."
                )

        # สร้างไดเรกทอรีปลายทางถ้ายังไม่มี
        if not os.path.exists(destination):
            os.makedirs(os.path.dirname(destination))

        shutil.move(source, destination)
        return {"message": "File moved successfully", "source": source, "destination": destination}
    