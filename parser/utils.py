import sqlite3
from functools import wraps
from typing import Callable


def get_conn(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("oped.db")
        r = func(*args, **kwargs, conn=conn)
        conn.close()
        return r

    return wrapper
