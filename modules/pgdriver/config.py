import os
import re

from pathlib import Path


class PostgresConfig:

    def __init__(
            self,
            host: str = "",
            port: str = "",
            dbname: str = "",
            connection_user: str = "",
            connection_pass: str = ""
        ):
        if len(port) > 0 and not re.match(r"^\d+$", port):
            raise ValueError(f"Port value must contains only digits. Now value is {port}")

        self.host = host
        self.port = port
        self.dbname = dbname
        self.connection_user = connection_user
        self.connection_pass = connection_pass


    def __repr__(self):
        return (
            f"Postgres connection config\n" +
            f"Host: {self.host}\n" +
            f"Port: {self.port}\n" +
            f"Database: {self.dbname}\n" +
            f"Connection username: {self.connection_user}\n" +
            f"Connection password: {self.connection_pass}\n"
        )


    @staticmethod
    def _clean_value(value: str):

        value = value.strip()

        # Очистка значения от кавычек
        quotes = ["\"", "'"]
        if len(value) > 2:
            if value[0] in quotes and value[0] == value[-1]:
                value = value[1:-1]

        return value


    @staticmethod
    # Обертка над os.getenv для очистки переменной от возможных спецсимволов
    def _get_env_var(name: str = ""):
        if len(name) == 0:
            return None

        var = os.getenv(name)

        if var is None:
            return None

        return var.strip()


    def load_from_env(self):
        variables_to_get = ["PG_HOST", "PG_PORT", "PG_DB_NAME", "PG_USER", "PG_PASSWORD"]
        loaded_variables = {}

        for var_name in variables_to_get:
            loaded_variables[var_name] = self._get_env_var(var_name)

        for var_name, var_value in loaded_variables.items():
            if not isinstance(var_value, str):
                raise TypeError(f"Trying to assign value of type {type(var_value)} to {var_name}. Must be str")

            if var_name == "PG_PORT":
                if not re.match(r"^\d+$", var_value):
                    raise ValueError(f"Port value must contains only digits. Now value is {var_value}")

        self.host = loaded_variables["PG_HOST"]
        self.port = loaded_variables["PG_PORT"]
        self.dbname = loaded_variables["PG_DB_NAME"]
        self.connection_user = loaded_variables["PG_USER"]
        self.connection_pass = loaded_variables["PG_PASSWORD"]


    def load_from_env_file(self, path: str):
        filepath = Path(path)

        if filepath.exists():
            with filepath.open(mode="r", encoding="utf-8") as file:
                for line in file:
                    clear_line = line.strip()

                    # Пропуск пустых строк
                    if not clear_line:
                        continue
                    # Пропуск комментариев
                    if clear_line.startswith("#"):
                        continue

                    arg, value = clear_line.split("=", maxsplit=1)

                    cleaned_arg = self._clean_value(arg)
                    cleaned_value = self._clean_value(value)

                    if cleaned_arg == "PG_HOST":
                        self.host = cleaned_value
                    elif cleaned_arg == "PG_PORT":
                        if not re.match(r"^\d+$", cleaned_value):
                            raise ValueError(f"Port value must contains only digits. Now value is {value}")
                        self.port = cleaned_value
                    elif cleaned_arg == "PG_DB_NAME":
                        self.dbname = cleaned_value
                    elif cleaned_arg == "PG_USER":
                        self.connection_user = cleaned_value
                    elif cleaned_arg == "PG_PASSWORD":
                        self.connection_pass = cleaned_value
                    else:
                        print(f"\033[1m\033[93m[WARN] load_from_env_file({path}) >>>>\033[0m Unknown config parameter {arg}")
        else:
            raise ValueError(f"Path {path} does not exists")
