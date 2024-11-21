# this module contains all the functions
# that help to improve the supervisor functionalities

from datetime import datetime

def datetime_formated() -> str:
    return datetime.now().strftime('%d-%m-%Y %H:%M:%S')