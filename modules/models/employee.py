from dataclasses import dataclass
from typing import Optional


@dataclass
class UpdateEmployee:
    employee_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    middle_name: Optional[str]
    position: Optional[str]
    hire_date: Optional[str]
    salary: Optional[int]
    manager_id: Optional[int]