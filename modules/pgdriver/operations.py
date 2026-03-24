import click
from tabulate import tabulate

from .pgdriver import read_pg_config
from .pgdriver import list_employees
from .data_generation import personal_data_generator

@click.group(name='edb')
def edb():
    read_pg_config("./.env/connection.env")


@edb.command()
def gen():
    headers = ["id", "last_name", "first_name", "position", "hire_date", "salary", "manager_id"]
    data = personal_data_generator()
    tab_data = [[item['last_name'], item['first_name'], item['middle_name']]
              for item in data]
    print(tabulate(tab_data, headers, tablefmt="github"))
    # print(data)

@edb.command()
def add():
    print("add edb")


@edb.command()
def upd():
    print("update edb")


@edb.command()
def rem():
    print("rem edb")


@edb.command()
def tree():
    print("tree edb")


@edb.command()
def seed():
    print("seed edb")


@edb.command()
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
    headers = ["id", "last_name", "first_name", "middle_name", "position", "hire_date", "salary", "manager_id"]
    print(tabulate(
        list_employees(limit, order, where),
        headers=headers,
        tablefmt="github"
    ))
