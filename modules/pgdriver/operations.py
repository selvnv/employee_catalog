import click

from datetime import datetime

from modules.utils.utils import print_employee_table
from .pgdriver import read_pg_config
from .pgdriver import list_employees, add_employee
from .data_generation import generate_employees_catalog


@click.group(name='edb')
def edb():
    read_pg_config("./.env/connection.env")


@edb.command(name="gen")
def gen():
    employee_list = generate_employees_catalog(100, ["ceo", "manager", "team_lead", "senior_developer", "developer"], 10_000, 100_000)
    employee_row = [employee.values() for employee in employee_list]
    print_employee_table(employee_row, headers=["last_name", "first_name", "middle_name", "position", "hire_date", "salary"])


@edb.command(name="add")
@click.option(
    "--hire-date", "-hd",
    default=datetime.now().strftime("%Y-%m-%d"),
    type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option(
    "--salary", "-s",
    required=True,
    type=click.FloatRange(min=0.0),
)
@click.option(
    "--manager", "-m",
    type=click.IntRange(min=1),
    default=None
)
def add(hire_date, salary, manager):
    print(add_employee("test","test","test","test", hire_date, salary, manager))


@edb.command(name="update")
def upd():
    print("update edb")


@edb.command(name="delete")
def rem():
    print("rem edb")


@edb.command()
def tree():
    print("tree edb")


@edb.command()
def seed():
    print("seed edb")


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
    print_employee_table(list_employees(limit, order, where))
