"""Submit file upload util domain"""

from typing import List
from pydantic import BaseModel


class FileUploaded(BaseModel):
    """Detail each file submit"""
    filename_tmp: str
    filename_original: str


class SubmitFilesDomain(BaseModel):
    """List file submit"""
    files: List[FileUploaded] = []
