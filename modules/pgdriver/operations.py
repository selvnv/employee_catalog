import click

from datetime import datetime

from click import IntRange, FloatRange

from .pgdriver import read_pg_config
from .pgdriver import list_employees, add_employee, delete_employees, update_employee, drop_data
from .data_generation import create_employees_catalog

from modules.utils.utils import print_employee_table_paged

from modules.models.employee import UpdateEmployee, InsertEmployee


@click.group(name='edb')
def edb():
    read_pg_config("./.env/connection.env")


@edb.command(name="gen")
@click.option("--count", "-c", nargs=1, type=IntRange(min=1), required=True,
    help="""
        Count of organization employees to generate
    """
)
@click.option("--salary", "-s", nargs=2, type=FloatRange(min=0.0), required=True,
    help="""
        Salary range: min_salary max_salary
    """)
@click.argument("positions", nargs=-1, type=str, required=True)
def gen(count, salary, positions):
    try:
        employee_list = create_employees_catalog(
            count, positions, min(salary), max(salary)
        )

        print(f"\033[1m\033[92m[COMPLETED]\033[0m Employee catalog data generated and saved into employees")

        print("\033[1m\033[94mSaved data\033[0m")
        print_employee_table_paged([employee.to_row() for employee in employee_list])

    except Exception as error:
        print(f"\033[1m\033[91m[ERROR] gen(...) >>>>\033[0m Error occurred while inserting. {repr(error)}")


@edb.command(name="add")
@click.option("--last-name", "-l", nargs=1, type=str, required=True)
@click.option("--first-name", "-f", nargs=1, type=str, required=True)
@click.option("--middle-name", nargs=1, type=str, default=None)
@click.option("--position", "-p", nargs=1, type=str, required=True)
@click.option(
    "--hire-date", "-h",
    default=datetime.now().strftime("%Y-%m-%d"),
    type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option(
    "--salary", "-s",
    required=True,
    type=click.FloatRange(min=0.0),
)
@click.option(
    "--manager-id", "-m",
    type=click.IntRange(min=1),
    default=None
)
def add(last_name, first_name, middle_name, position, hire_date, salary, manager_id):
    try:
        employee = InsertEmployee(
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            position=position,
            hire_date=hire_date,
            salary=salary,
            manager_id=manager_id,
            employee_id=None
        )
        employee_id = add_employee(employee)
        print(f"\033[1m\033[92m[COMPLETED]\033[0m Employee {last_name} {first_name} added with ID: {employee_id}")
    except Exception as error:
        print(f"\033[1m\033[91m[ERROR] add(...) >>>>\033[0m {error}")


@edb.command(name="update")
@click.option("--last-name", "-l", nargs=1, type=str, required=False, default=None)
@click.option("--first-name", "-f", nargs=1, type=str, required=False, default=None)
@click.option("--middle-name", nargs=1, type=str, required=False, default=None)
@click.option("--position", "-p", nargs=1, type=str, required=False, default=None)
@click.option("--hire-date", "-h", nargs=1, type=str, required=False, default=None)
@click.option("--salary", "-s", nargs=1, type=float, required=False, default=None)
@click.option("--manager-id", "-m", nargs=1, type=IntRange(min=-1), required=False,
    metavar="ID",
    show_default=True,
    default=0,
    help="""
        if set 0, then doesn't make any changes. if set -1, then set field manager_id as NULL\n                        
    """
)
@click.argument("employee_id", type=IntRange(min=1), required=True, nargs=1)
def upd(last_name, first_name, middle_name, position, hire_date, salary, manager_id, employee_id):
    update_data = UpdateEmployee(
        employee_id=employee_id,
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
        position=position,
        hire_date=hire_date,
        salary=salary,
        manager_id=manager_id,
    )
    print(update_data)
    try:
        update_info = update_employee(update_data)
        print(
            f"\033[1m\033[92m[COMPLETED]\033[0m Update employee with ID: {employee_id}\n" +
            f"\033[1m\033[94m[INFO]\033[0m Current data is {update_info}"
        )
    except Exception as error:
        print(f"\033[1m\033[91m[ERROR] upd(...) >>>>\033[0m {error}")


@edb.command(name="delete")
@click.argument("employee_ids", nargs=-1, required=True, type=int)
def rem(employee_ids):
    print("rem edb", employee_ids)
    try:
        deleted_employee_ids = delete_employees(employee_ids)
        print(f"\033[1m\033[92m[COMPLETED]\033[0m Delete employees with ID: {deleted_employee_ids}")
    except Exception as error:
        print(f"\033[1m\033[91m[ERROR] rem(...) >>>>\033[0m {error}")


@edb.command(name="list")
@click.option("--limit", "-l", nargs=1, type=int, default=None)
@click.option("--order", "-o", nargs=1, type=str, default=None)
@click.option("--where", "-w", nargs=3, type=str, default=None, multiple=True,
    help="""
    <field> <comparison_operator> <value>
    Filter rows by any condition
    
    Usage examples:\n 
    \tlast_name eq \"Johnson\"
    
    \tsalary gt 1000
    
    Available comparison operators:\n
        eq - equal\n
        ne - not equal\n
        gt - greater than\n
        ge - greater or equal\n
        lt - less than\n
        le - less or equal\n
    """
)
def lst(limit, order, where):
    print_employee_table_paged(list_employees(limit, order, where))


@edb.command()
def tree():
    print("tree edb")


@edb.command()
@click.confirmation_option(prompt='Are you sure you want to drop the db data?')
def drop():
    try:
        drop_data()
        print(f"\033[1m\033[92m[COMPLETED]\033[0m Drop all data")
    except Exception as error:
        print(f"\033[1m\033[91m[ERROR] rem(...) >>>>\033[0m {error}")