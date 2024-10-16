import sys, os

FRONTEND_URL = "http://localhost:5173"
OAUTH2_INFO = {
    "client_id": "6LEtFNLwpjRvQSCsyJ2V8jL8E9vgOI9YykyIjR84",
    "client_secret": "iAQ3nHW1tSxJOVYkChPTmpAj1IGdDcVSCzvvrncVRK3TIPJYCos3qPn1KLDZeFqzjtlZhpJ4PqM0XRmzWpsQ41zHaSrEiCQf5jEljYuUjXlS2GerwdPHcJei11NtVhZu",
}


def error_message(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    lineno = exc_tb.tb_lineno
    file_path = exc_tb.tb_frame.f_code.co_filename
    file_name = os.path.basename(file_path)
    return f"[{file_name}_{lineno}] {str(e)}"
