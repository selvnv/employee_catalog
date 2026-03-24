from modules.pgdriver.config import POSTGRES_CONFIG
from modules.pgdriver.pgdriver import read_pg_config

def main():
    read_pg_config("./.env/connection.env")
    with POSTGRES_CONFIG.get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            print(cursor.fetchall())

if __name__ == "__main__":
    main()
