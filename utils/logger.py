import logging
import os
import sys
import uuid
from flask import has_request_context, g, request
from pythonjsonlogger import jsonlogger

class RequestIdFilter(logging.Filter):
    """
    Filter that injects the current request ID from Flask's request context
    into the log record attributes.
    """
    def filter(self, record):
        if has_request_context():
            if not hasattr(g, 'request_id'):
                g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
            record.request_id = g.request_id
        else:
            record.request_id = 'N/A'
        return True

def setup_logger():
    # Read log level from environment (default: INFO)
    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clean up existing handlers to prevent duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    # Create stdout handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Format log output as JSON
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(pathname)s %(lineno)d'
    )
    handler.setFormatter(formatter)
    
    root_logger.addHandler(handler)
    
    # Add filter to inject request correlation ID
    req_filter = RequestIdFilter()
    root_logger.addFilter(req_filter)
    
    # Also ensure flask.app logger does not add duplicate handlers
    logging.getLogger("flask.app").handlers = []
    
    return root_logger

# Initialize logger instance
logger = setup_logger()
