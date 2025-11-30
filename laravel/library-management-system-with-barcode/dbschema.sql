DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) NOT NULL UNIQUE,
    user_name VARCHAR(100) NOT NULL,
    user_email VARCHAR(100) NOT NULL UNIQUE,
    user_password TEXT NOT NULL
);

DROP TABLE IF EXISTS books;
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id varchar(100) NOT NULL UNIQUE,
    book_title varchar(200) NOT NULL,
    book_author varchar(200) NOT NULL,
    book_isbn varchar(20) NULL,
    book_lang_code varchar(4) NOT NULL,
    book_copy integer not null
);

DROP TABLE IF EXISTS languages;
CREATE TABLE languages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lang_code varchar(4) NOT NULL UNIQUE,
    lang_description varchar(200) NOT NULL
);
insert into languages(lang_code,lang_description) values ('TA','Tamil');
insert into languages(lang_code,lang_description) values ('EN','English');
insert into languages(lang_code,lang_description) values ('ES','Spanish');
insert into languages(lang_code,lang_description) values ('TE','Telugu');

DROP TABLE IF EXISTS bookloandetail;
CREATE TABLE bookloandetail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id varchar(100) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    loaned_date date NOT NULL,
    expected_return_date  date not null,
    returned_date date null,
    loan_status varchar(4) not null
);

DROP TABLE IF EXISTS userroles;
CREATE TABLE userroles (    
    role_id varchar(20) PRIMARY KEY NOT NULL,
    role_description varchar(100) NOT NULL
);
insert into userroles values('ADMIN','Administrator');
insert into userroles values('MEMBR','Member');
insert into userroles values('SUSER','Super User');
insert into userroles values('USER','User');
insert into userroles values('GUST','Guest User');

DROP TABLE IF EXISTS userrolemapping;
CREATE TABLE userrolemapping (   
    user_id VARCHAR(50) NOT NULL,
    role_id varchar(20) NOT NULL
);

DROP TABLE IF EXISTS loanstatus;
CREATE TABLE loanstatus (   
    status_id VARCHAR(4) NOT NULL,
    status_description varchar(50) NOT NULL
);
insert into loanstatus values('LND','Loaned');
insert into loanstatus values('REQ','Requested');
insert into loanstatus values('RVD','Received');
insert into loanstatus values('REJ','Rejected');


drop view if exists v_bookloansummary;
create view v_bookloansummary as 
select book_id,count(1) as b_count from bookloandetail
where loan_status in('LND','REQ')
group by book_id;

drop view if exists v_bookavailablesummary;
create view v_bookavailablesummary as 
select b.book_id, b.book_copy-COALESCE(s.b_count,0) as a_count from books b left outer join v_bookloansummary s
on b.book_id=s.book_id;

DROP VIEW IF EXISTS v_bookloansummaryadmn;
CREATE VIEW v_bookloansummaryadmn as select book_id,count(1) as b_count from bookloandetail where loan_status in('LND') group by book_id;

drop view if exists v_bookavailablesummaryadmn;
create view v_bookavailablesummaryadmn as 
select b.book_id, b.book_copy-COALESCE(s.b_count,0) as a_count from books b left outer join v_bookloansummaryadmn s
on b.book_id=s.book_id;

drop view if exists v_booklistforloanapproval;
create view v_booklistforloanapproval as 
select d.id, b.book_id,b.book_title,l.lang_description,b.book_author, a.a_count as availablecopies from books b inner join v_bookavailablesummaryadmn a 
    on b.book_id=a.book_id inner join languages l 
    on b.book_lang_code=l.lang_code
	inner join bookloandetail d
	on d.book_id=b.book_id and d.loan_status='REQ';


drop view if exists v_loanedbooks;
create view v_loanedbooks as 
select d.id, b.book_id,b.book_title,l.lang_description,d.loaned_date,u.user_name as loanedby from books b  inner join languages l 
    on b.book_lang_code=l.lang_code
	inner join bookloandetail d
	on d.book_id=b.book_id 
	inner join users u on d.user_id = u.user_id
	where d.loan_status='LND';