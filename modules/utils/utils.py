from tabulate import tabulate

DEFAULT_TABLE_HEADERS = ["id", "last_name", "first_name", "middle_name", "position", "hire_date", "salary", "manager_id"]

def print_employee_table(row_data,
                         headers: list = DEFAULT_TABLE_HEADERS):
    print(tabulate(
        row_data,
        headers=headers,
        tablefmt="rounded_grid"
    ))