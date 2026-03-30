import random

from datetime import datetime

from mimesis import Person
from mimesis import Locale
from mimesis.enums import Gender

from numpy import logspace

from modules.models.employee import InsertEmployee
from modules.pgdriver.pgdriver import add_employees

DEFAULT_ORG_STRUCTURE = {
    "ceo": {
        "position_name": "ceo",
        "count": 1,
        "min_salary": 500_000,
        "max_salary": 800_000
    },
    "manager": {
        "position_name": "manager",
        "count": 250,
        "min_salary": 350_000,
        "max_salary": 500_000
    },
    "team_lead": {
        "position_name": "team_lead",
        "count": 1_500,
        "min_salary": 300_000,
        "max_salary": 500_000
    },
    "senior_developer": {
        "position_name": "senior_developer",
        "count": 12_500,
        "min_salary": 200_000,
        "max_salary": 450_000
    },
    "developer": {
        "position_name": "developer",
        "count": 35_749,
        "min_salary": 100_000,
        "max_salary": 250_000
    }
}


SALARY_SPREAD_COEFFICIENT = 0.2
MIN_SALARY_SPREAD_COEFFICIENT = 0.05

DEFAULT_EXP_GEN_BASE = 5
DEFAULT_PROB_DIST_GEN_BASE = 2.5

DEFAULT_MIN_HIRE_DATE = "2020-01-01"
DEFAULT_MAX_HIRE_DATE = datetime.now().strftime("%Y-%m-%d")


DEFAULT_MIN_SALARY = 80_000
DEFAULT_MAX_SALARY = 500_000


def random_date(start: str, end: str) -> str | None:
    """
       Generate random date in format YYYY-MM-DD

       Args:
           start: Min date (YYYY-MM-DD)
           end: Max date (YYYY-MM-DD)

       Returns:
           Random date in format YYYY-MM-DD OR None if exception raised
       """

    if not start or not end:
        print(f"\033[1m\033[93m[WARN] random_date(...) >>>>\033[0m the boundaries of the date range are not set. ")
        return None

    try:
        start_timestamp = int(datetime.fromisoformat(start).timestamp())
        end_timestamp = int(datetime.fromisoformat(end).timestamp())

        random_timestamp = random.randint(start_timestamp, end_timestamp)

        return datetime.fromtimestamp(random_timestamp).strftime("%Y-%m-%d")
    except Exception as error:
        print(f"\033[1m\033[93m[WARN] random_date(...) >>>>\033[0m {error}. ")
        return None


def generate_probability_distribution(level_count: int, growth_rate: float = DEFAULT_PROB_DIST_GEN_BASE) -> list:
    """
        Generates a normalized discrete exponential probability distribution
        It is useful for modeling hierarchical distributions,
        such as employee counts across organizational levels

        Different growth_rate allows make distribution more flatt or pyramidal
        Bigger growth_rate -> function grows faster
        Smaller growth_rate -> function grows slower

        Formula:
            p(i) = base^i / sum(base^j for j in 0..n-1)
            where:
                i — index of the element (0-based)
                n — total number of elements
                base — exponential growth factor (> 0)

        Args:
            level_count: count of hierarchy levels
            growth_rate: base of exponential distribution

        Returns:
            list of generated distribution values for level_count levels
    """
    if growth_rate <= 1:
        raise ValueError(f"growth_rate must be greater than 1, but got {growth_rate}")

    if level_count <= 0:
        return []

    # Формирование "весов" распределения (пропорций количества сотрудников в зависимости от количества уровней)
    # По сути - во сколько раз каждый следующий уровень содержит больше сотрудников, чем первый
    level_weights = [growth_rate ** i for i in range(level_count)]
    weights_sum = sum(level_weights)

    # Нормализация получившихся весов к вероятностному распределению.
    # Каждое значение можно интерпретировать как долю сотрудников от общего их числа
    # Чем ниже уровень → тем больше сотрудников
    distribution = [level_weight / weights_sum for level_weight in level_weights]

    return distribution


def generate_exponential_scale(number: int, base: int = DEFAULT_EXP_GEN_BASE) -> list:
    """
        Generates a normalized monotonic-growth exponential (logarithmic) scale over the interval (0, 1]
        It is useful for modeling quantities that grow non-linearly,
        such as salary levels across hierarchy levels

        Formula:
            y(i) = base^(t_i - 1), where t_i ∈ [0, 1]
            where:
                t_i ∈ [0, 1] are evenly spaced points
                base — exponential base (> 1)
                n — number of generated values

        Note:
            This is not a probability distribution (sum != 1), but the scale represents relative magnitudes (e.g., salary levels)

        Args:
            base: base of logarithmic scale
            number: number of values to generate

        Returns:
            list of
    """

    if base <= 1:
        raise ValueError(f"base must be greater than 1, but got {base}")

    if number <= 0:
        raise ValueError(f"number must be greater than 0, but got {number}")

    # Генерация точек с экспоненциально растущими интервалами между друг другом
    log_scale_values = logspace(start = 0.0, stop = 1.0, base=base, num=number)

    # Нормализация значений (приведение к диапазону значений 0-1)
    normalized_values = [x / base for x in log_scale_values]

    return normalized_values


def generate_salary_ranges(min_salary: int, max_salary: int, ranges_count: int = 5) -> list:
    salary_log_scale = generate_exponential_scale(ranges_count)

    salary_ranges = []
    for i in range(ranges_count):
        # Определяется точка на шкале заработной платы, относительно которой будут определены ее границы
        center = min_salary + (max_salary - min_salary) * salary_log_scale[i]

        # Определяется разброс начальной и максимальной заработной платы
        # Разброс уменьшается с возрастанием должности
        spread_coefficient = SALARY_SPREAD_COEFFICIENT * (1.0 - salary_log_scale[i])
        delta = center * (spread_coefficient if spread_coefficient > 0 else MIN_SALARY_SPREAD_COEFFICIENT)

        low = int(max(min_salary, center - delta))
        high = int(min(max_salary, center + delta))

        salary_ranges.append((low, high))

    # Полученный массив разворачивается, т.к. иерархия сотрудников "от старшего к младшему" (у первых, соответственно, зарплата больше)
    return salary_ranges[::-1]


def generate_random_salary(min_salary: int, max_salary: int) -> int:
    return random.randint(min_salary, max_salary)


def calc_org_structure(
        employee_count: int = 10,
        position_names: list = None,
        min_salary: int = DEFAULT_MIN_SALARY,
        max_salary: int = DEFAULT_MAX_SALARY) -> dict | None:
    """
        Generates org_structure for employee catalog in format
        {
            "pos_name": {
                "position_name": pos_name
                "count": A
                "min_salary": B,
                "max_salary": C
            }
            ...
        }

        where A, B, C - int number

        Args:
            employee_count: count of employees in catalog
            position_names: names of employee positions
            min_salary: min salary for employee catalog
            max_salary: max salary for employee catalog

        Returns:
            dict representation of employee catalog
    """

    if employee_count <= 0:
        return None

    if position_names is None or len(position_names) == 0:
        return None

    position_distribution = generate_probability_distribution(len(position_names))
    salary_ranges = generate_salary_ranges(min_salary, max_salary, len(position_names))

    # Определение количества сотрудников в структуре
    employee_count_by_position = []
    for index in range(len(position_names)):
        # Вычисление количество сотрудников с данной должностью
        # Если доступно для распределения меньше сотрудников - берем весь доступный остаток
        # Минимум 1 сотрудник на позицию
        employees_by_position =  max(1, min(employee_count, int(employee_count * position_distribution[index])))
        employee_count_by_position.append(employees_by_position)

        # Получение оставшегося количества сотрудников, доступных для распределения
        employee_count -= employees_by_position

    # Если есть не распределенный остаток, добавить его к нижнему уровню структуры сотрудников
    if employee_count > 0:
        employee_count_by_position[-1] += employee_count

    employee_structure = {}
    for index in range(len(position_names)):
        employee_structure[position_names[index]] = {
            "position_name": position_names[index],
            "count": employee_count_by_position[index],
            "min_salary": salary_ranges[index][0],
            "max_salary": salary_ranges[index][1]
        }

    return employee_structure


def generate_employee_data(person_generator: Person, position_info: dict, min_hire_date: str, max_hire_date: str, manager_id: int = None) -> InsertEmployee | None:

    if not person_generator:
        print(f"\033[1m\033[93m[WARN] generate_employee_data(...) >>>>\033[0m person_generator is empty. ")
        return None

    if not position_info:
        print(f"\033[1m\033[93m[WARN] generate_employee_data(...) >>>>\033[0m position_info is empty. ")
        return None

    if not all(key in position_info for key in ["position_name", "count", "min_salary", "max_salary"]):
        print(
            f"\033[1m\033[93m[WARN] generate_employee_data(...) >>>>\033[0m" +
            f"position_info must contain [\"count\", \"min_salary\", \"max_salary\"] keys, but contains only {position_info.keys()}. "
        )
        return None

    gender = random.choice(list(Gender))
    person = InsertEmployee(
        last_name=person_generator.last_name(gender=gender),
        first_name=person_generator.first_name(gender=gender),
        middle_name=person_generator.patronymic(gender=gender),
        position=position_info["position_name"],
        hire_date=random_date(min_hire_date,  max_hire_date),
        salary=generate_random_salary(position_info["min_salary"], position_info["max_salary"]),
        employee_id=None,
        manager_id=manager_id
    )

    return person


def create_employees_catalog(
        total_count: int,
        position_names: list[str],
        min_salary: int = DEFAULT_MIN_SALARY,
        max_salary: int = DEFAULT_MAX_SALARY,
        min_hire_date: str = DEFAULT_MIN_HIRE_DATE,
        max_hire_date: str = DEFAULT_MAX_HIRE_DATE) -> list:
    """
        Generates and inserts a list of employees with random personal data (with specified restrictions)

        Args:
            total_count: count of employees in catalog
            position_names: names of employee positions
            min_salary: min salary for employee catalog
            max_salary: max salary for employee catalog
            min_hire_date: min hire date for employee catalog
            max_hire_date: max hire date for employee catalog

        Returns:
            list of employees with random personal data
    """
    if total_count <= 0:
        return []

    if not position_names:
        return []

    org_structure = calc_org_structure(total_count, position_names, min_salary, max_salary)

    person_generator = Person(locale=Locale.RU)
    employees = []
    insertion_start_index = 0
    manager_ids = []
    employee_ids = []

    for position in position_names:
        for _ in range(org_structure[position]["count"]):
            person = generate_employee_data(
                person_generator,
                org_structure[position],
                min_hire_date,
                max_hire_date,
                random.choice(manager_ids) if manager_ids else None
            )
            employees.append(person)

        # На следующем уровне иерархии используются id текущего уровня
        manager_ids = add_employees(employees[insertion_start_index:])

        employee_ids.extend(manager_ids)
        insertion_start_index = len(employees)

    # Дополнение данных сотрудников их id
    for person, emp_id in zip(employees, employee_ids):
        person.employee_id = emp_id

    return employees