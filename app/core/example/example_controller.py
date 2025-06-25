"""Example controller"""

import json
from typing import List

from fastapi import File, Response, UploadFile, HTTPException

from app.core.example.domain import ExampleDomain,ExampleSubmitUploadDomain
from app.util.log_util import set_application_log

from .example_manager import ExampleManager

LOGGER = set_application_log(__name__)


class ExampleController:
    """Example Controller"""

    logger = None
    manager = None

    def __init__(self):
        self.logger = LOGGER
        self.manager = ExampleManager()

    def get_process(self):
        """GET example"""
        self.logger.debug("get process")
        response = None

        try:
            results = self.manager.process()
            self.logger.debug(results)
            response = Response(
                content=json.dumps(results),
                status_code=200,
                media_type="application/json",
            )
        except KeyError as e:
            error_message = {"message": str(e)}
            response = Response(
                content=json.dumps(error_message),
                status_code=400,
                media_type="application/json",
            )
        except Exception as e:
            # Handle all other exceptions
            error_message = {"message": str(e)}
            response = Response(
                content=json.dumps(error_message),
                status_code=500,
                media_type="application/json",
            )
            self.logger.error("Exception occurred", exc_info=True)

        return response

    def post_process(self, criteria: ExampleDomain):
        """Example post"""
        self.logger.debug("get process")
        response = None

        result = {"result": criteria.word}
        response = Response(
            content=json.dumps(result), status_code=200, media_type="application/json"
        )

        return response

    async def upload_files(self,files: List[UploadFile] = File(...)):
        """Upload file"""
        self.logger.debug("upload file")

        response = None

        try :
            self.logger.debug("send process")
            response = await self.manager.upload_files(files)
        except HTTPException as e:
            error_message = {"message": str(e)}
            response = Response(
                content=json.dumps(error_message),
                status_code=400,
                media_type="application/json",
            )
        except Exception as e:
            # Handle all other exceptions
            error_message = {"message": str(e)}
            response = Response(
                content=json.dumps(error_message),
                status_code=500,
                media_type="application/json",
            )
            self.logger.error("Exception occurred", exc_info=True)

        return response

    def submit_files_upload(self,criteria:ExampleSubmitUploadDomain):
        """submit file"""
        response = None

        try :
            self.logger.debug("send process")
            response = self.manager.submit_files_upload(criteria)
        except Exception as e:
            # Handle all other exceptions
            error_message = {"message": str(e)}
            response = Response(
                content=json.dumps(error_message),
                status_code=500,
                media_type="application/json",
            )
            self.logger.error("Exception occurred", exc_info=True)

        return response
            