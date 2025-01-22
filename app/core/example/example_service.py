from app.util.log_util import setup_logger

LOGGER = setup_logger('example_service')

class ExampleService:
    
    logger = None
    manager = None
    
    def __init__(self):
        self.logger = LOGGER
    
    def process(self):
        return {
            "message": "This is an example response."
        }