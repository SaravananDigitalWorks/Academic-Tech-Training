DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) NOT NULL UNIQUE,
    user_name VARCHAR(100) NOT NULL,
    user_email VARCHAR(100) NOT NULL UNIQUE,
    user_password TEXT NOT NULL
);
DROP TABLE IF EXISTS timeslots;
CREATE TABLE timeslots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time_code VARCHAR(20) NOT NULL UNIQUE,
    start_time VARCHAR(10) NOT NULL,
    end_time VARCHAR(10) NOT NULL
);

DROP TABLE IF EXISTS menus;
CREATE TABLE menus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_code varchar(20) NOT NULL UNIQUE,
    menu_name varchar(100) NOT NULL,
    menu_price real NOT NULL,
    menu_description TEXT NOT NULL
);

DROP TABLE IF EXISTS menutime;
CREATE TABLE menutime (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_code varchar(20) NOT NULL,
    time_code VARCHAR(20) NOT NULL
);
DROP TABLE IF EXISTS menuorder;
CREATE TABLE menuorder (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id varchar(50) UNIQUE NOT NULL,
    order_token integer NOT NULL,
    order_date datetime not null

);

DROP TABLE IF EXISTS oderdetail;
CREATE TABLE oderdetail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id varchar(50) NOT NULL,
    menu_code varchar(20) NOT NULL,
    quantity integer not null

);



