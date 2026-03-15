CREATE TABLE employees (
    id BIGSERIAL PRIMARY KEY,
    last_name VARCHAR(200),
    first_name VARCHAR(200),
    patronymic VARCHAR(200),
    position VARCHAR(200) NOT NULL,
    hire_date DATE NOT NULL,
    salary DOUBLE PRECISION NOT NULL CHECK (salary >= 0),
    manager_id BIGINT REFERENCES employees(id)
);