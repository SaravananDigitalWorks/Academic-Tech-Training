DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) NOT NULL UNIQUE,
    user_name VARCHAR(100) NOT NULL,
    user_email VARCHAR(100) NOT NULL UNIQUE,
    user_password TEXT NOT NULL
);
DROP TABLE IF EXISTS departments;
CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_code VARCHAR(10) NOT NULL UNIQUE,
    department_name VARCHAR(100) NOT NULL,
    department_description TEXT NOT NULL
);

DROP TABLE IF EXISTS employees;
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id varchar(10) NOT NULL UNIQUE,
    employee_first_name varchar(100) NOT NULL,
    employee_last_name varchar(100) NOT NULL, 
    employee_email varchar(100) NOT NULL,
    employee_gender varchar(1) NOT NULL,
    employee_department varchar(1) NULL,
    employee_image varchar(100) NULL
);

