import logging
import time
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class CustomLoggerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
        request.start_datetime = datetime.now()

    def process_response(self, request, response):
        # Calculate the duration of the request
        duration = time.time() - request.start_time

        # Get method, URL, and request start time
        method = request.method
        url = request.get_full_path()
        request_time = request.start_datetime.strftime("%Y-%m-%d %H:%M:%S")

        # Check if `response` has `data` attribute and safely access message
        message_text = ""
        if hasattr(response, "data") and response.data is not None:
            message_text = response.data.get("message", "")

        # Create log message
        message = (
            f"[{request_time}] {method} {url} - Status: {response.status_code} - "
            f"Duration: {duration:.2f}s - Message: {message_text}"
        )

        # Log the detailed information
        logger.info(message)

        return response

    def process_exception(self, request, exception):
        # Calculate the duration of the request
        duration = time.time() - request.start_time

        # Get method, URL, and request start time
        method = request.method
        url = request.get_full_path()
        request_time = request.start_datetime.strftime("%Y-%m-%d %H:%M:%S")

        # Create log message for the exception
        message = (
            f"[{request_time}] {method} {url} - Exception: {exception} - "
            f"Duration: {duration:.2f}s"
        )

        # Log the exception details
        logger.error(message, exc_info=True)
