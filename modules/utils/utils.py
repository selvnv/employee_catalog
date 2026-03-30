import math

from tabulate import tabulate

DEFAULT_TABLE_HEADERS = ["id", "last_name", "first_name", "middle_name", "position", "hire_date", "salary", "manager_id"]

def print_employee_table(row_data,
                         headers: list = DEFAULT_TABLE_HEADERS):
    print(tabulate(
        row_data,
        headers=headers,
        tablefmt="rounded_grid"
    ))


def print_employee_table_paged(row_data,
                         headers: list = DEFAULT_TABLE_HEADERS,
                         page_size: int = 8):
    total_rows = len(row_data)
    total_pages = math.ceil(total_rows / page_size)

    current_page = 0

    while current_page < total_pages:
        start_row = current_page * page_size
        end_row = min(start_row + page_size, total_rows)

        selection = row_data[start_row:end_row]

        print(tabulate(
            selection,
            headers=headers,
            tablefmt="rounded_grid"
        ))

        user_choice = input(f"\nPage {current_page + 1} of {total_pages}. Rows {end_row} of {total_rows}. \nPress \033[1m\033[92menter\033[0m to continue (\033[1m\033[92mq\033[0m to skip\\exit): ")
        if user_choice == "q":
            break

        current_page += 1