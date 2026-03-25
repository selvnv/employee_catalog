import random
from datetime import datetime
from mimesis import Person
from mimesis import Locale
from mimesis.enums import Gender
from numpy import logspace

COMPANY_POSITION_RATIO = {
    "ceo": 1,
    "manager": 250,
    "team_lead": 1_500,
    "senior_developer": 12_500,
    "developer": 35_749
}


SALARY_RANGE = {
    "ceo": (500_000, 800_000),
    "manager": (350_000, 500_000),
    "team_lead": (200_000, 500_000),
    "senior_developer": (300_000, 500_000),
    "developer": (100_000, 250_000)
}


SALARY_SPREAD_COEFFICIENT = 0.2
MIN_SALARY_SPREAD_COEFFICIENT = 0.05

DEFAULT_EXP_GEN_BASE = 5
DEFAULT_PROB_DIST_GEN_BASE = 2.5

DEFAULT_MIN_RANDOM_DATE = "1971-01-01"
DEFAULT_MAX_RANDOM_DATE = datetime.now().strftime("%Y-%m-%d")


def random_date(start: str = DEFAULT_MIN_RANDOM_DATE,
                end: str = DEFAULT_MAX_RANDOM_DATE) -> str | None:
    """
       Generate random date in format YYYY-MM-DD

       Args:
           start: Min date (YYYY-MM-DD)
           end: Max date (YYYY-MM-DD)

       Returns:
           Random date in format YYYY-MM-DD OR None if exception raised
       """

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


def generate_employee_data(person_generator: Person, position: str) -> dict | None:

    if not person_generator:
        return None

    if not position or position not in COMPANY_POSITION_RATIO:
        return None

    gender = random.choice(list(Gender))
    person_data = {
        "id": "?",
        "last_name": person_generator.last_name(gender=gender),
        "first_name": person_generator.first_name(gender=gender),
        "middle_name": person_generator.patronymic(gender=gender),
        "position": position,
        "hire_date": random_date("2020-01-01", "2026-01-01"),
        "salary": "?",
        "manager_id": "?"
    }

    return person_data


def generate_employees_catalog(total_count: int = 10):
    if total_count <= 0:
        return []

    # Количество сотрудников, которое можно сгенерировать
    employees_left = total_count
    # При генерации сохраняются пропорции количества сотрудников на определенном уровне иерархии
    ratio = total_count / sum(COMPANY_POSITION_RATIO.values())

    fact_position_ratio = {
        # CEO всегда один
        "ceo": 1,
    }

    employees_left = max(0, employees_left - fact_position_ratio["ceo"])

    fact_position_ratio["manager"] = min(employees_left, int(COMPANY_POSITION_RATIO["manager"] * ratio))
    employees_left = max(0, employees_left - fact_position_ratio["manager"])

    fact_position_ratio["team_lead"] = min(employees_left, int(COMPANY_POSITION_RATIO["team_lead"] * ratio))
    employees_left = max(0, employees_left - fact_position_ratio["team_lead"])

    fact_position_ratio["senior_developer"] = min(employees_left, int(COMPANY_POSITION_RATIO["senior_developer"] * ratio))
    employees_left = max(0, employees_left - fact_position_ratio["senior_developer"])

    fact_position_ratio["developer"] = min(employees_left, int(COMPANY_POSITION_RATIO["developer"] * ratio))
    employees_left = max(0, employees_left - fact_position_ratio["developer"])

    person_generator = Person(locale=Locale.RU)
    for position, count in fact_position_ratio.items():
        for _ in range(count):
            generate_employee_data(person_generator, position)


    person_list = generate_employee_data(count=total_count)