from dataclasses import dataclass
from typing import Optional


@dataclass
class InsertEmployee:
    employee_id: Optional[int]
    first_name: str
    last_name: str
    middle_name: Optional[str]
    position: str
    hire_date: str
    salary: int
    manager_id: Optional[int]


    def to_row(self):
        return (
            self.employee_id,
            self.first_name,
            self.last_name,
            self.middle_name,
            self.position,
            self.hire_date,
            self.salary,
            self.manager_id,
        )

    def to_insertion_row(self):
        return (
            self.last_name,
            self.first_name,
            self.middle_name,
            self.position,
            self.hire_date,
            self.salary,
            self.manager_id,
        )


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