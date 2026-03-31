from psycopg2.extras import execute_values

from typing import Sequence

from .config import POSTGRES_CONFIG

from modules.models.employee import UpdateEmployee, InsertEmployee


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


def read_config_from_env() -> None:
    POSTGRES_CONFIG.load_from_env()


def check_connection():
    return POSTGRES_CONFIG.healthcheck()


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


def add_employee(employee: InsertEmployee) -> int:
    if not employee or not isinstance(employee, InsertEmployee):
        return -1

    try:
            with POSTGRES_CONFIG.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO employees (last_name, first_name, middle_name, position, hire_date, salary, manager_id) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        employee.to_insertion_row(),
                    )

                    # cursor.fetchone() returns tuple like (id,)
                    employee_id = cursor.fetchone()[0]
                    return employee_id
    except Exception as error:
        print(f"\033[1m\033[91m[ERROR] add_employee(...) >>>>\033[0m {error}")
        raise


def add_employees(
        employees: list[InsertEmployee],
) -> list[int]:
    if not employees or len(employees) == 0:
        print(f"\033[1m\033[91m[WARN] add_employees(...) >>>>\033[0m Employee list is empty. Nothing to add")
        return []

    for employee in employees:
        if not employee or not isinstance(employee, InsertEmployee):
            raise ValueError(f"add_employees(...) >>>> Wrong data or data type.\n Employee list items must be InsertEmployee type but got {type(employee)}")

    try:
        with POSTGRES_CONFIG.get_connection() as connection:
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO employees (
                        last_name, first_name, middle_name, 
                        position, hire_date, salary, manager_id
                    ) 
                    VALUES %s
                    RETURNING id
                """

                # Приведение данных от модели к массиву данных для вставки
                employees_data = [employee.to_insertion_row() for employee in employees]
                execute_values(cursor, query, employees_data, template="(%s, %s, %s, %s, %s, %s, %s)")

                employee_ids = [row[0] for row in cursor.fetchall()]
                return employee_ids
    except Exception as error:
        print(f"\033[1m\033[91m[ERROR] add_employees(...) >>>>\033[0m {error}")
        raise


def delete_employees(
        employee_ids: Sequence[int],
):
    if not employee_ids or len(employee_ids) == 0:
        return []

    try:
        deleted_employee_ids = []
        with POSTGRES_CONFIG.get_connection() as connection:
            with connection.cursor() as cursor:
                query = """
                    DELETE FROM employees
                    WHERE id = ANY(%s)
                    RETURNING id
                """

                cursor.execute(query, (list(employee_ids),))

                deleted_employee_ids = [row[0] for row in cursor.fetchall()]
                return deleted_employee_ids
    except Exception as error:
        print(f"\033[1m\033[91m[ERROR] delete_employee(...) >>>>\033[0m {error}")
        raise


def generate_update_query(employee_data: UpdateEmployee):
    args = []

    set_clauses = []

    if employee_data.last_name is not None:
        set_clauses.append("last_name = %s")
        args.append(employee_data.last_name)
    if employee_data.first_name is not None:
        set_clauses.append("first_name = %s")
        args.append(employee_data.first_name)
    if employee_data.middle_name is not None:
        set_clauses.append("middle_name = %s")
        args.append(employee_data.middle_name)
    if employee_data.position is not None:
        set_clauses.append("position = %s")
        args.append(employee_data.position)
    if employee_data.hire_date is not None:
        set_clauses.append("hire_date = %s")
        args.append(employee_data.hire_date)
    if employee_data.salary is not None:
        set_clauses.append("salary = %s")
        args.append(employee_data.salary)
    if employee_data.manager_id:
        # manager_id == -1, установить в NULL
        # manager_id == 0, ничего не делать
        # manager_id > 0, установить заданный manager_id
        if employee_data.manager_id == -1:
            set_clauses.append("manager_id = NULL")
        else:
            set_clauses.append("manager_id = %s")
            args.append(employee_data.manager_id)

    if not set_clauses:
        raise ValueError("generate_update_query(...) >>>> Nothing to update. All arguments are empty")

    query = f"""
        UPDATE employees
        SET {",".join(set_clauses)}
        WHERE id = %s
        RETURNING *
    """
    args.append(employee_data.employee_id)

    return query, args


def update_employee(employee: UpdateEmployee) -> tuple:
    if not employee.employee_id or employee.employee_id <= 0:
        return ()

    try:
        with POSTGRES_CONFIG.get_connection() as connection:
            with connection.cursor() as cursor:
                query, args = generate_update_query(employee)

                cursor.execute(query, args)
                response = cursor.fetchone()[0]
                return response
    except Exception as error:
        print(f"\033[1m\033[91m[ERROR] update_employee(...) >>>>\033[0m {error}")
        raise


def drop_data():
    try:
        with POSTGRES_CONFIG.get_connection() as connection:
            with connection.cursor() as cursor:
                query = """
                    DELETE FROM employees
                """
                cursor.execute(query)
    except Exception as error:
        print(f"\033[1m\033[91m[ERROR] drop_data(...) >>>>\033[0m {error}")
        raise


def select_hierarchy(top_position: str):
    if not top_position:
        return []

    try:
        with POSTGRES_CONFIG.get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""
                    WITH RECURSIVE hierarchy AS (
                        SELECT id, manager_id, last_name, first_name, middle_name, position
                        FROM employees
                        WHERE position = %s
                    
                        UNION
                    
                        SELECT e.id, e.manager_id, e.last_name, e.first_name, e.middle_name, e.position
                        FROM employees AS e
                        JOIN hierarchy AS h ON h.id = e.manager_id
                    )
                
                    SELECT * FROM hierarchy;
                """

                cursor.execute(query, (top_position,))

                employees = [employee_row for employee_row in cursor.fetchall()]
                return employees
    except Exception as error:
        print(f"\033[1m\033[91m[ERROR] select_hierarchy(...) >>>>\033[0m {error}")
        raise