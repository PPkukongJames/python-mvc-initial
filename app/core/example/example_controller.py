from app.util.log_util import setup_logger
from fastapi import Response
import json
from .example_manager import ExampleManager
from .domain import ExampleDomain

LOGGER = setup_logger('example_controller')

class ExampleController:
    
    logger = None
    manager = None
    
    def __init__(self):
        self.logger = LOGGER
        self.manager = ExampleManager()
    
    def get_process(self):
        self.logger.debug("get process")
        response = None
        
        try :
            results = self.manager.process()
            self.logger.debug(results)
            response = Response(
                content=json.dumps(results),
                status_code=200,
                media_type='application/json'
            )
        except KeyError as e:
            error_message = {'message': str(e)}
            response = Response(
                content=json.dumps(error_message),
                status_code=400,
                media_type='application/json'
            )
        except Exception as e:
            # Handle all other exceptions
            error_message = {'message': str(e)}
            response = Response(
                content=json.dumps(error_message),
                status_code=500,
                media_type='application/json'
            )
            self.logger.error('Exception occurred', exc_info=True)

        return response
    
    def post_process(self,criteria:ExampleDomain):
        self.logger.debug("get process")
        response = None
        
        result = {
            'result':criteria.word
        }
        response = Response(
                content=json.dumps(result),
                status_code=200,
                media_type='application/json'
            )
        
        return response