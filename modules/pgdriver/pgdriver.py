import psycopg2
from .config import POSTGRES_CONFIG

ALLOWED_ORDER_BY_FIELDS = {"id", "last_name", "first_name", "position", "hire_date", "salary"}
ALLOWED_COMPARISON_FIELDS = {"id", "last_name", "first_name", "middle_name", "position", "hire_date", "salary", "manager_id"}
ALLOWED_COMPARISON_OPERATORS={
    "eq": "=",
    "ne": "!=",
    "gt": ">",
    "lt": "<",
    "ge": ">=",
    "le": "<="
}


def read_pg_config(config_path: str) -> None:
    if not config_path:
        return

    try:
        POSTGRES_CONFIG.load_from_env_file(config_path)
    except Exception as e:
        print(e)


# input: (('last_name', 'eq', 'Doe'), ('salary', 'ge', '1000'))
# output: ("last_name = %s AND salary >= %s", ["Doe", "1000"])
# returns format string and params for substitution
def parse_where_conditions(where_conditions: tuple = None) -> tuple:
    if not where_conditions:
        return "", []

    final_format_string = ""
    format_values = []
    for condition in where_conditions:
        field_name, comparison_operator, value = condition
        if field_name not in ALLOWED_COMPARISON_FIELDS:
            print(f"\033[1m\033[93m[WARN] parse_where_conditions(...) >>>>\033[0m field name {field_name} is not allowed in WHERE clause. Skipped")
            continue

        if comparison_operator not in ALLOWED_COMPARISON_OPERATORS:
            print(f"\033[1m\033[93m[WARN] parse_where_conditions(...) >>>>\033[0m comparison operator {comparison_operator} is not allowed in WHERE clause. Skipped")
            continue

        format_string = f"{field_name} {ALLOWED_COMPARISON_OPERATORS[comparison_operator]} %s"
        if not final_format_string:
            final_format_string = " WHERE " + format_string
        else:
            final_format_string += f" AND {format_string}"

        format_values.append(value)

    return final_format_string, format_values


def add_order_by(field_name: str) -> str:
    if field_name in ALLOWED_ORDER_BY_FIELDS:
        return f" ORDER BY {field_name}"
    return " ORDER BY id"


def add_limit(limit: int = None) -> str:
    if limit:
        return f" LIMIT {limit}"
    return ""


def list_employees(limit: int = None, order_field: str = None, where_conditions: tuple = None) -> list:
    try:
        if POSTGRES_CONFIG and POSTGRES_CONFIG.healthcheck():
            with POSTGRES_CONFIG.get_connection() as connection:
                with connection.cursor() as cursor:
                    format_where_string, where_params = parse_where_conditions(where_conditions)
                    cursor.execute(
                        "SELECT * FROM employees"
                        + format_where_string
                        + add_order_by(order_field)
                        + add_limit(limit),
                        where_params
                    )

                    return cursor.fetchall()
    except Exception as error:
        print(f"\033[1m\033[93m[WARN] list_employees(...) >>>>\033[0m {error}")

    return []
