from app.util.log_util import setup_logger
from .example_service import ExampleService

LOGGER = setup_logger('example_manager')

class ExampleManager:
    
    logger = None
    manager = None
    
    def __init__(self):
        self.logger = LOGGER
        self.service = ExampleService()
    
    def process(self):
        return self.service.process()