from flask import Flask, render_template, request, send_file, redirect ,url_for,session,jsonify,flash
import sqlite3
import os
import qrcode
import json
from io import BytesIO
import base64
import hashlib,logging,sys
import random
import io
import datetime
import barcode
from barcode.writer import ImageWriter
from barcode import Code39

app = Flask(__name__)
app.secret_key = 'sdfhbsdcuiusdfiuhwefmnewn2139872137234jbnlkrh8ewyry74rdsfknkdsnfy3439sdfnksdfkjwefrfi34r9i34'
DATABASE = 'lms.db'

def create_db_file(dbname):
    if os.path.isfile(dbname):
        return
    f=open(dbname, "x")

def get_db_connection():
    create_db_file(DATABASE)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db_connection()
        if  os.path.getsize(DATABASE) == 0:
            with app.open_resource('dbschema.sql', mode='r') as f:
                db.cursor().executescript(f.read())                
            db.commit()
            db.close()
            insert_adminuser()

def insert_adminuser():
    u_id="admin"
    u_name="Admin"
    u_password="Test@123"
    u_email="admin@mydomain.com"
    u_role_id="ADMIN"
    hashed_password = hashlib.sha256(u_password.encode()).hexdigest()
    try:
        db = get_db_connection()
        db.execute("INSERT INTO users (user_id, user_name, user_email, user_password) VALUES (?, ?, ?, ?)", (u_id,u_name, u_email, hashed_password))
        db.execute("INSERT INTO userrolemapping (user_id, role_id) VALUES (?, ?)", (u_id,u_role_id))
        db.commit()
        db.close()
        print("Record inserted successfully.")
    except Exception as e:
        print("Error:", e)

def create_user(userid, username, email, password):
    db = get_db_connection()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    db.execute("INSERT INTO users (user_id, user_name, user_email, user_password) VALUES (?, ?, ?, ?)", (userid, username, email, hashed_password))
    db.commit()
    db.close()

def create_user_role(userid, roleid):
    db = get_db_connection()
    db.execute("INSERT INTO userrolemapping (user_id, role_id) VALUES (?, ?)", (userid, roleid))
    db.commit()
    db.close()

def authenticate_user(userid, password):
    db = get_db_connection()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    userdata=db.execute("SELECT user_id,user_name FROM users WHERE user_id=? AND user_password=?", (userid, hashed_password,)).fetchone()
    db.close()
    return userdata

def getUserRole(userid):
    db = get_db_connection()
    userdata=db.execute("SELECT role_id FROM userrolemapping WHERE user_id=?", (userid,)).fetchone()
    db.close()
    return userdata
def change_password(useid, old_password, new_password):
    db = get_db_connection()
    hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
    hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
    db.execute("UPDATE users SET user_password=? WHERE user_id=? AND user_password=?", (hashed_new_password, useid, hashed_old_password))
    db.commit()
    db.close()
def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
def isDataPresent(tableName,ColumnName,ColumnValue):
    status=False
    db = get_db_connection()
    sqlQuery="SELECT * FROM " + tableName + " WHERE " + ColumnName + "=?"
    dbdata=db.execute(sqlQuery, (ColumnValue,)).fetchone()
    db.close()
    if dbdata:
        status=True
    return status
def redirectToLogin():
    if 'logged_in' not in session:
        return render_template('loginForm.html')
    
@app.route('/authenticate', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user=authenticate_user(username,password)  
        userrole=getUserRole(username)     
        if user is not None:
            session['logged_in'] = True
            session['userid'] = user['user_id']
            session['username'] = user['user_name']
            session['userrole'] = userrole['role_id']
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password','danger')
    return render_template('loginForm.html')
@app.route('/about', methods=['GET','POST'])
def list_about():
    return render_template('about.html')
@app.route('/contact', methods=['GET','POST'])
def list_contact():
    return render_template('contact.html')
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('userid', None)
    session.pop('username', None)
    session.pop('userrole', None)
    
    return redirect(url_for('index'))

@app.route('/')
def index():   
    return render_template('welcome.html')
@app.route('/users')
def list_users():
    if 'logged_in' not in session:
        return render_template('loginForm.html')
    db = get_db_connection()
    users = db.execute('SELECT id,user_id,user_name,user_email from users').fetchall()
    db.close()
    return render_template('users.html', users=users)

def getLanguages():
    db = get_db_connection()
    result_data = db.execute('SELECT * from languages').fetchall()
    db.close()
    return result_data

def getTableData(tablename):
    db = get_db_connection()
    result_data = db.execute("SELECT * from " + tablename).fetchall()
    db.close()
    return result_data

@app.route('/book/add', methods=['GET','POST'])
def open_add_book():
    result_data = getLanguages()
    return render_template('book/newbook.html',languages=result_data)

@app.route('/newuser', methods=['GET','POST'])
def open_new_user():
    userroles=getTableData('userroles')
    return render_template('newUserForm.html',userroles=userroles)

def getBookList():
    db = get_db_connection()
    books_data = db.execute('select b.*,l.lang_description, a.a_count from books b inner join v_bookavailablesummary a on b.book_id=a.book_id inner join languages l on b.book_lang_code=l.lang_code').fetchall()
    db.close()
    return books_data

def getBookDetail(id):
    db = get_db_connection()
    sqlQuery = """select b.*,l.lang_description, a.a_count from books b inner join v_bookavailablesummary a 
    on b.book_id=a.book_id inner join languages l 
    on b.book_lang_code=l.lang_code where b.id=?"""
    book_data = db.execute(sqlQuery,(id,)).fetchone()
    db.close()
    return book_data

@app.route('/books', methods=['GET','POST'])
def list_books():
    books_data=getBookList()
    return render_template('book/books.html',books=books_data)

@app.route('/admin/loanrequests', methods=['GET','POST'])
def show_loan_requests():
    books_data=getTableData('v_booklistforloanapproval')
    return render_template('admin/loanrequests.html',books=books_data)

@app.route('/admin/loan/approve/<id>', methods=['GET','POST'])
def approve_loan_requests(id):
    approveLoanRequest(id)
    flash("Loan request has been approved successfully !!!",'success')
    books_data=getTableData('v_booklistforloanapproval')
    return render_template('admin/loanrequests.html',books=books_data)

@app.route('/admin/loan/reject/<id>', methods=['GET','POST'])
def reject_loan_requests(id):
    rejectLoanRequest(id)
    flash("Loan request has been rejected successfully !!!",'success')
    books_data=getTableData('v_booklistforloanapproval')
    return render_template('admin/loanrequests.html',books=books_data)



@app.route('/admin/return', methods=['GET','POST'])
def show_books_for_receive():
    books_data=getTableData('v_loanedbooks')
    return render_template('admin/returns.html',books=books_data)

@app.route('/admin/book/receive/<id>', methods=['GET','POST'])
def receive_book(id):
    acceptReturn(id)
    flash("Receive request has been submitted successfully !!!",'success')
    books_data=getTableData('v_loanedbooks')
    return render_template('admin/returns.html',books=books_data)


def getBookCode(id):
    db = get_db_connection()
    book_data = db.execute('SELECT book_id FROM books where id=?',(id,)).fetchone()
    db.close()
    return book_data['book_id']

def getAvailableCopies(bookid):
    availablecopies=0
    db = get_db_connection()
    book_data = db.execute("SELECT a_count FROM v_bookavailablesummary where book_id=?",(bookid,)).fetchone()
    availablecopies=book_data['a_count']   
    db.close()
    return availablecopies

def bookLoanRequest(bookid,userid):
    db = get_db_connection()
    loaned_date=datetime.date.today()
    expected_return_date= loaned_date + datetime.timedelta(days=10)
    loan_status="REQ"
    db.execute('INSERT INTO bookloandetail(book_id,user_id,loaned_date,loan_status,expected_return_date) VALUES (?, ?, ?, ?, ?)', (bookid,userid,loaned_date,loan_status,expected_return_date))
    db.commit()
    db.close()

def approveLoanRequest(id):
    db = get_db_connection()
    loaned_date=datetime.date.today()
    expected_return_date= loaned_date + datetime.timedelta(days=10)
    loan_status="LND"
    db.execute("update bookloandetail set expected_return_date=?, loan_status=? WHERE id=? and loan_status='REQ'",(expected_return_date,loan_status,id))
    db.commit()
    db.close()

def acceptReturn(id):
    db = get_db_connection()
    return_date=datetime.date.today()
    loan_status="RVD"
    db.execute("update bookloandetail set returned_date=?, loan_status=? WHERE id=? and loan_status='LND'",(return_date,loan_status,id))
    db.commit()
    db.close()

def rejectLoanRequest(id):
    db = get_db_connection()
    loan_status="REJ"
    db.execute("update bookloandetail set loan_status=? WHERE id=? and loan_status='REQ'",(loan_status,id))
    db.commit()
    db.close()

@app.route('/book/loan/<id>', methods=['GET','POST'])
def loan_book(id):    
    book_code=getBookCode(id)
    bookLoanRequest(book_code,session['userid'])
    flash("Your request has been submitted successgully !!! Please contact Librarian to get the book", 'success')
    books_data=getBookList()  
    return render_template('book/books.html',books=books_data)

@app.route('/book/view/<id>', methods=['GET','POST'])
def view_book_detail(id):
    book_data=getBookDetail(id)
    code_39 = Code39(book_data['book_id'], writer=ImageWriter())
    # Save the barcode to a BytesIO object
    barcode_buffer = io.BytesIO()
    code_39.write(barcode_buffer)
    image_base64 = base64.b64encode(barcode_buffer.getvalue()).decode('utf-8')
    barcode_img_data = f"data:image/jpg;base64,{image_base64}"
    return render_template('book/bookdetail.html',book=book_data,barcode_img_data=barcode_img_data)


@app.route('/addUser', methods=['GET','POST'])
def add_user():
    user_id = request.form['userid']
    user_name = request.form['username']
    user_email = request.form['email']
    user_password = request.form['password']
    user_role = request.form['user_role']
    create_user(user_id,user_name,user_email,user_password)
    create_user_role(user_id,user_role)
    return redirect(url_for('list_users'))

@app.route('/book/create', methods=['GET','POST'])
def add_book():
    book_id = request.form['book_id']
    book_title = request.form['book_title']
    book_isbn = request.form['book_isbn']
    book_author = request.form['book_author']
    book_language = request.form['book_language']
    book_copy = request.form['book_copy']

    if isDataPresent('books','book_id',book_id):
        flash('Book id already used for another book','danger')
        return redirect(url_for('open_add_book', **request.form))
   
    db = get_db_connection()
    db.execute('INSERT INTO books (book_id,book_title,book_author,book_lang_code,book_isbn,book_copy) VALUES (?, ?, ?, ?, ?, ?)', (book_id,book_title,book_author,book_language,book_isbn,book_copy))
    db.commit()
    db.close()
    flash("Book record created successfully!!!",'success')
    return redirect(url_for('list_books'))


@app.route('/book/edit/<id>')
def open_edit_book(id):
    db = get_db_connection()
    cur=db.cursor()
    book_data=cur.execute("SELECT * FROM books WHERE id=?", (id,)).fetchone()
    db.commit()
    db.close()
    result_data = getLanguages()
    return render_template('book/editbook.html', book=book_data,languages=result_data)

@app.route('/book/update/<id>', methods=['GET','POST'])
def update_book(id):
    book_id = request.form['book_id']
    book_title = request.form['book_title']
    book_isbn = request.form['book_isbn']
    book_author = request.form['book_author']
    book_language = request.form['book_language']
    book_copy = request.form['book_copy']
    db = get_db_connection()
    cur=db.cursor()
    cur.execute("UPDATE books SET book_id=?, book_title=?, book_isbn=?, book_author=?, book_lang_code=? , book_copy=? WHERE id=?", (book_id,book_title,book_isbn,book_author,book_language,book_copy,id,))
    db.commit()
    db.close()
    flash("Book record Updated successfully!!!",'success')
    return redirect(url_for('list_books'))

@app.route('/book/delete/<id>')
def delete_book(id):
    db = get_db_connection()
    cur=db.cursor()
    cur.execute("DELETE FROM books WHERE id=?", (id,))
    db.commit()
    db.close()
    flash("Book record Deleted successfully!!!",'danger')
    return redirect(url_for('list_books'))

@app.route('/deleteUser/<id>')
def del_user(id):
    db = get_db_connection()
    cur=db.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect(url_for('list_users'))

if __name__ == '__main__':
    init_db()  # Ensure our database and table are created
    app.run(debug=True)