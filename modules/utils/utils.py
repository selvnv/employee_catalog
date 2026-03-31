import math

from tabulate import tabulate


DEFAULT_TABLE_HEADERS = ["id", "last_name", "first_name", "middle_name", "position", "hire_date", "salary", "manager_id"]


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

        user_choice = input(
            f"\nPage {current_page + 1} of {total_pages}." +
            f"Rows {end_row} of {total_rows}. \n" +
            f"Press \033[1m\033[92menter\033[0m to continue (\033[1m\033[92mq\033[0m to skip\\exit): "
        )
        if user_choice == "q":
            break

        current_page += 1


def build_employee_tree(row_data):
    nodes = {}

    for row in row_data:
        if len(row) < 6:
            continue

        employee_id = row[0]
        # Создание ноды с ключом == id сотрудника
        nodes[employee_id] = {
            "id": employee_id,
            "title": f"{row[2]} {row[3]} {row[4] if row[4] else ""} {row[5]}",
            "children": []
        }

    # На старте все ноды считаются корневыми
    # И исключаются из списка по мере определения их как child_nodes
    root_ids = set(nodes.keys())

    for row in row_data:
        employee_id = row[0]
        manager_id = row[1]

        # Если нода является дочерней и родительская нода есть в выборке
        if manager_id and manager_id in nodes:
            # Добавляем родительской ноде потомка (текущий узел)
            nodes[manager_id]["children"].append(nodes[employee_id])
            root_ids.discard(employee_id)

    return [nodes[root_id] for root_id in root_ids]


# Обход дерева сотрудников в глубину
def print_employee_tree(employee_subtree, prefix=""):
    for i, node in enumerate(employee_subtree):
        # Проверка - нода последний лист в поддереве
        is_last_node = i == len(employee_subtree) - 1

        connector = "└── " if is_last_node else "├── "
        print(prefix + connector + node["title"])

        # Если нода последняя, то после └── не должно быть │
        child_node_prefix = prefix + ("    " if is_last_node else "│   ")

        print_employee_tree(node["children"], child_node_prefix)
