from config import settings
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from contextlib import asynccontextmanager


pool = ConnectionPool(
    conninfo="",
    kwargs={
        "host":settings.host,
        "port":settings.port,
        "dbname":settings.name,
        "user":settings.user,
        "password":settings.password,
        "row_factory" : dict_row
    },

    min_size=1,
    max_size=10,
    open= False,
)

@asynccontextmanager
async def lifespan(app):
    pool.open(wait=True)
    try:
        yield
    finally:
        pool.close()

def get_connection():
    with pool.connection() as connection:
        yield connection