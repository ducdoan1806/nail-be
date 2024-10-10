import sys, os

FRONTEND_URL = "http://localhost:5173"


def error_message(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    lineno = exc_tb.tb_lineno
    file_path = exc_tb.tb_frame.f_code.co_filename
    file_name = os.path.basename(file_path)
    return f"[{file_name}_{lineno}] {str(e)}"
