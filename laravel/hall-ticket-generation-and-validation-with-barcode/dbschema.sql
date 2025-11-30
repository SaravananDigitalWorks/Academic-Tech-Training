DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) NOT NULL UNIQUE,
    user_name VARCHAR(100) NOT NULL,
    user_email VARCHAR(100) NOT NULL UNIQUE,
    user_password TEXT NOT NULL
);
DROP TABLE IF EXISTS centers;
CREATE TABLE centers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    center_code varchar(10) NOT NULL UNIQUE,
    center_name varchar(100) NOT NULL
);
DROP TABLE IF EXISTS students;
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name varchar(100) NOT NULL,
    reg_number varchar(20) NOT NULL UNIQUE,
    center_code varchar(10) NOT NULL,
    verification_code TEXT NOT NULL,
    image_name varchar(150) null
);

