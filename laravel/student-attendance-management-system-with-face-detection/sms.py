from flask import Flask, render_template, request, send_file, redirect ,url_for,session,jsonify,flash
import sqlite3
import os
from io import BytesIO
import base64
import hashlib,logging,sys
import io

app = Flask(__name__)
app.secret_key = '457884758745jhertjjhert874957ejthdnflnsdflnsdk;fjhsdfh'
DATABASE = 'lms.db'
student_image_prefix='STUDENT_'

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
    hashed_password = hashlib.sha256(u_password.encode()).hexdigest()
    try:
        db = get_db_connection()
        db.execute("INSERT INTO users (user_id, user_name, user_email, user_password) VALUES (?, ?, ?, ?)", (u_id,u_name, u_email, hashed_password))
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

def authenticate_user(userid, password):
    db = get_db_connection()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    userdata=db.execute("SELECT user_id,user_name FROM users WHERE user_id=? AND user_password=?", (userid, hashed_password,)).fetchone()
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

def getColumnData(tableName,ColumnName,id):
    result=''
    db = get_db_connection()
    sqlQuery="SELECT "+ ColumnName +" FROM " + tableName + " WHERE id=?"
    dbdata=db.execute(sqlQuery, (id,)).fetchone()
    db.close()
    if dbdata:
        result=dbdata[0]
    return result


@app.route('/addUser', methods=['GET','POST'])
def add_user():
    user_id = request.form['userid']
    user_name = request.form['username']
    user_email = request.form['email']
    user_password = request.form['password']
    create_user(user_id,user_name,user_email,user_password)
    return redirect(url_for('list_users'))
def redirectToLogin():
    if 'logged_in' not in session:
        return render_template('loginForm.html')
@app.route('/authenticate', methods=['GET', 'POST'])

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user=authenticate_user(username,password)       
        if user is not None:
            session['logged_in'] = True
            session['username'] = user['user_name']
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
    session.pop('username', None)
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


@app.route('/newuser', methods=['GET','POST'])
def open_new_user():
    return render_template('newUserForm.html')


@app.route('/deleteUser/<id>')
def del_user(id):
    db = get_db_connection()
    cur=db.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect(url_for('list_users'))

"""
SMS routs
"""

@app.route('/departments')
def list_departments():
    if 'logged_in' not in session:
        return render_template('loginForm.html')
    db = get_db_connection()
    result_data = db.execute('SELECT * FROM departments').fetchall()
    db.close()
    return render_template('department/departments.html', departments=result_data)

@app.route('/department/new')
def open_new_departnet():
    if 'logged_in' not in session:
        return render_template('loginForm.html')
    return render_template('department/newdepartment.html')

@app.route('/department/add', methods=['GET','POST'])
def add_department():
    department_code = request.form['department_code']
    department_name = request.form['department_name']
    department_description = request.form['department_description']
    department_description=department_description.strip()
    department_code = department_code.upper()
    if isDataPresent('departments','department_code',department_code):
        flash('Department code already present','error')
        return redirect(url_for('open_new_departnet'))
    db = get_db_connection()
    db.execute('INSERT INTO departments (department_code,department_name,department_description) VALUES (?, ?, ?)', (department_code,department_name,department_description))
    db.commit()
    db.close()
    return redirect(url_for('list_departments'))

@app.route('/department/delete/<id>')
def delete_department(id):
    db = get_db_connection()
    cur=db.cursor()
    cur.execute("DELETE FROM departments WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect(url_for('list_departments'))


@app.route('/department/edit/<id>')
def open_edit_department(id):
    db = get_db_connection()
    cur=db.cursor()
    result_data=cur.execute("SELECT * FROM departments WHERE id=?", (id,)).fetchone()
    db.commit()
    db.close()
    return render_template('department/editdepartment.html', department=result_data)

@app.route('/department/update/<id>', methods=['GET','POST'])
def update_department(id):
    try:
        department_code = request.form['department_code']
        department_name = request.form['department_name']
        department_description = request.form['department_description']
        department_description=department_description.strip()
        department_code = department_code.upper()
        db = get_db_connection()
        cur=db.cursor()
        cur.execute("UPDATE departments SET department_code=?, department_name=?, department_description=? WHERE id=?", (department_code,department_name,department_description,id,))
        db.commit()
        db.close()
        flash('Record uodated successfully!','success')
    except Exception as e:
            flash('Error Occurred','danger')
    finally:
        return redirect(url_for('list_departments'))
    
@app.route('/employees')
def list_employees():
    if 'logged_in' not in session:
        return render_template('loginForm.html')
    db = get_db_connection()
    result_data = db.execute('SELECT * FROM employees').fetchall()
    db.close()
    return render_template('employee/employees.html', employees=result_data)

@app.route('/employee/new')
def open_new_employee():
    if 'logged_in' not in session:
        return render_template('loginForm.html')
    db = get_db_connection()
    result_data = db.execute('SELECT * FROM departments').fetchall()
    db.close()
    return render_template('employee/newemployee.html',departments=result_data)

@app.route('/employee/add', methods=['GET','POST'])
def add_employee():
    try:
        employee_id = request.form['employee_id']
        employee_first_name = request.form['employee_first_name']
        employee_last_name = request.form['employee_last_name']
        employee_email = request.form['employee_email']
        employee_gender = request.form['employee_gender']
        employee_department = request.form['employee_department']
        employee_id = employee_id.upper()
        if isDataPresent('employees','employee_id',employee_id):
            flash('Employee id already present','error')
            return redirect(url_for('open_new_employee'))
        db = get_db_connection()
        last_record_id=db.execute('INSERT INTO employees (employee_id, employee_first_name,employee_last_name,employee_email,employee_gender,employee_department) VALUES (?, ?, ?, ?, ?, ?)', (employee_id, employee_first_name,employee_last_name,employee_email,employee_gender, employee_department)).lastrowid
        db.commit()
        db.close()
        image_name=str(last_record_id)
        if 'employee_image' in request.files: 
            print('File Present')       
            file = request.files['employee_image']
            if file.filename == '':
                return jsonify({'error': 'No selected file'})

            if file:
                file_extension = os.path.splitext(file.filename)
                filename = image_name + file_extension[1]

                # Save the file to the images directory
                file.save(os.path.join('images', filename)) 
        
        db = get_db_connection()
        cur=db.cursor()
        cur.execute("UPDATE employees SET employee_image=? WHERE id=?", (filename,last_record_id,))
        db.commit()
        db.close()
        flash('Employee record created sucessfully!','success')
    except Exception as e:
        flash(f"An error occurred: {str(e)}",'danger')
        
    finally:          
        return redirect(url_for('list_employees'))
    

@app.route('/employee/edit/<id>', methods=['GET','POST'])
def open_edit_employee(id):
    db = get_db_connection()
    cur=db.cursor()
    employee=cur.execute("SELECT * FROM employees WHERE id=?", (id,)).fetchone()
    db.commit()
    db.close()    
    db = get_db_connection()
    result_data_department = db.execute('SELECT * FROM departments').fetchall()
    db.close()
    return render_template('employee/editemployee.html', employee=employee, departments=result_data_department)

@app.route('/employee/update/<id>', methods=['GET','POST'])
def update_employee(id):
    try:
        employee_id = request.form['employee_id']
        employee_first_name = request.form['employee_first_name']
        employee_last_name = request.form['employee_last_name']
        employee_email = request.form['employee_email']
        employee_gender = request.form['employee_gender']
        employee_department = request.form['employee_department']
        employee_id = employee_id.upper()
        
        db = get_db_connection()
        db.execute('update employees set employee_id=?, employee_first_name=?,employee_last_name=?,employee_email=?,employee_gender=?,employee_department=? WHERE id=?', (employee_id, employee_first_name,employee_last_name,employee_email,employee_gender, employee_department,id,))
        db.commit()
        db.close()
        image_name=str(id)
        if 'employee_image' in request.files:                   
            file = request.files['employee_image']
            if file.filename == '':
                return jsonify({'error': 'No selected file'})
            if file:
                print('File Present')
                file_extension = os.path.splitext(file.filename)
                filename = image_name + file_extension[1]

                # Save the file to the images directory
                file.save(os.path.join('images', filename))         
                db = get_db_connection()
                cur=db.cursor()
                cur.execute("UPDATE employees SET employee_image=? WHERE id=?", (filename,id,))
                db.commit()
                db.close()
        flash('Employee record updated sucessfully!','success')
    except Exception as e:
        flash(f"An error occurred: {str(e)}",'danger')        
    finally:          
        return redirect(url_for('list_employees'))
   

@app.route('/employee/delete/<id>')
def delete_employee(id):
    image_name=str(getColumnData('employees','employee_image',id))
    try:        
        if image_name != '':
            delete_file(os.path.join('images', image_name))
        db = get_db_connection()
        cur=db.cursor()
        cur.execute("DELETE FROM employees WHERE id=?", (id,))
        db.commit()
        db.close()
        flash('Record Deleted successfully','success')
    except Exception as e:
        flash(f"An error occurred: {str(e)}",'danger')
        
    finally:          
        return redirect(url_for('list_employees'))
    
@app.route('/employee/view/<id>', methods=['GET','POST'])
def open_view_employee(id):
    db = get_db_connection()
    cur=db.cursor()
    employee=cur.execute("SELECT * FROM employees WHERE id=?", (id,)).fetchone()
    db.commit()
    db.close()    
    image_name=os.path.join('images', employee['employee_image'])
    image_bytes=BytesIO()
    with open(image_name, 'rb') as f:
        # Read the contents of the file
        image_bytes = f.read()
        image_buffer = io.BytesIO()
        image_buffer.write(image_bytes)
        image_buffer.seek(0)
        image_base64 = base64.b64encode(image_buffer.getvalue()).decode('utf-8')
        user_img_data = f"data:image/jpg;base64,{image_base64}"

    db = get_db_connection()
    result_data_department = db.execute('SELECT * FROM departments').fetchall()
    db.close()
    return render_template('employee/viewemployee.html', employee=employee, departments=result_data_department,user_img_data=user_img_data)



"""
SMS routs end
"""

if __name__ == '__main__':
    init_db()  # Ensure our database and table are created
    app.run(debug=True)