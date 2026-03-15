from modules.pgdriver.config import PostgresConfig

def main():
    postgres_config = PostgresConfig()
    postgres_config.load_from_env_file("./.env/connection.env")
    print(postgres_config)


if __name__ == "__main__":
    main()
