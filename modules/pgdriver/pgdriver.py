import psycopg2
from .config import POSTGRES_CONFIG

def read_pg_config(configpath: str) -> None:
    if not configpath:
        return

    try:
        POSTGRES_CONFIG.load_from_env_file(configpath)
    except Exception as e:
        print(e)


