# utils.py
from datetime import datetime

def get_today():
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")