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

app = Flask(__name__)
app.secret_key = 'sdfhbsdcuiusdfiuhwefmnewn2139872137234jbnlkrh8ewyry74rdsfknkdsnfy3439sdfnksdfkjwefrfi34r9i34'
DATABASE = 'students.db'
def dd(variable):
    print(variable)


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
            flash("invalid username or password",'danger')
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
@app.route('/students')
def list_students():
    if 'logged_in' not in session:
        return render_template('loginForm.html')
    db = get_db_connection()
    students = db.execute('SELECT s.id,s.reg_number,s.student_name,s.center_code,c.center_name FROM students s inner join centers c on s.center_code=c.center_code').fetchall()
    db.close()
    return render_template('students.html', students=students)
@app.route('/users')
def list_users():
    if 'logged_in' not in session:
        return render_template('loginForm.html')
    db = get_db_connection()
    users = db.execute('SELECT id,user_id,user_name,user_email from users').fetchall()
    db.close()
    return render_template('users.html', users=users)

@app.route('/student/new', methods=['GET','POST'])
def open_add_student():
    db = get_db_connection()    
    centers = db.execute('SELECT * FROM centers').fetchall()
    db.close()
    return render_template('newstudent.html',centers=centers)
@app.route('/center/new', methods=['GET','POST'])
def open_add_center():
    return render_template('new_center.html')

@app.route('/newuser', methods=['GET','POST'])
def open_new_user():
    return render_template('newUserForm.html')

@app.route('/centers', methods=['GET','POST'])
def list_centers():
    db = get_db_connection()
    centers = db.execute('SELECT * FROM centers').fetchall()
    db.close()
    return render_template('centers.html',centers=centers)

@app.route('/student/add', methods=['GET','POST'])
def add_student():
    student_name = request.form['student_name']
    reg_number = request.form['reg_number']
    center_code = request.form['center_code']
    if isDataPresent('students','reg_number',reg_number):
        flash('Register number already present','error')
        return redirect(url_for('open_add_student', **request.form))
    long_random_number = str(random.randint(10**(20-1), 10**20 - 1))
    db = get_db_connection()
    last_record_id=db.execute('INSERT INTO students (student_name, reg_number,center_code,verification_code) VALUES (?, ?, ?, ?)', (student_name, reg_number,center_code, long_random_number)).lastrowid
    db.commit()
    db.close()
    image_name=str(last_record_id)
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:       
        file_extension = os.path.splitext(file.filename)
        filename = image_name + file_extension[1]

        # Save the file to the images directory
        file.save(os.path.join('images', filename))    

        db = get_db_connection()
        db.execute('UPDATE students set image_name=? WHERE id=?', (filename, last_record_id,))
        db.commit()
        db.close()          
    return redirect(url_for('list_students'))

@app.route('/student/edit/<id>', methods=['GET','POST'])
def open_edit_student(id):
    db = get_db_connection()
    student=db.execute("SELECT s.id,s.reg_number,s.student_name,s.center_code,c.center_name,s.verification_code FROM students s inner join centers c on s.center_code=c.center_code WHERE s.id=?", (id,)).fetchone()     
    db.close()
    db = get_db_connection()    
    centers = db.execute('SELECT * FROM centers').fetchall()
    db.close()
    return render_template('modifystudent.html', student=student,centers=centers)

@app.route('/student/update/<id>', methods=['GET','POST'])
def update_student(id):
    student_name = request.form['student_name']
    reg_number = request.form['reg_number']
    center_code = request.form['center_code']
    db = get_db_connection()
    db.execute('UPDATE students SET student_name=?,center_code=? WHERE id=?', (student_name,center_code, id,))
    db.commit()
    db.close()
    image_name=str(id)
    file = request.files['file']
    if file:       
        file_extension = os.path.splitext(file.filename)
        filename = image_name + file_extension[1]

        # Save the file to the images directory
        file.save(os.path.join('images', filename)) 

        db = get_db_connection()
        db.execute('UPDATE students set image_name=? WHERE id=?', (filename, id,))
        db.commit()
        db.close()          
    return redirect(url_for('list_students'))

@app.route('/addUser', methods=['GET','POST'])
def add_user():
    user_id = request.form['userid']
    user_name = request.form['username']
    user_email = request.form['email']
    user_password = request.form['password']
    create_user(user_id,user_name,user_email,user_password)
    return redirect(url_for('list_users'))

@app.route('/center/add', methods=['GET','POST'])
def add_center():
    center_code = request.form['center_code']
    center_name = request.form['center_name']
    center_code = center_code.upper()
    if isDataPresent('centers','center_code',center_code):
        flash('Center already present','error')
        return redirect(url_for('open_add_center', **request.form))
    db = get_db_connection()
    db.execute('INSERT INTO centers (center_code,center_name) VALUES (?, ?)', (center_code,center_name))
    db.commit()
    db.close()
    return redirect(url_for('list_centers'))


@app.route('/center/edit/<id>')
def open_edit_center(id):
    db = get_db_connection()
    cur=db.cursor()
    center=cur.execute("SELECT * FROM centers WHERE id=?", (id,)).fetchone()
    db.commit()
    db.close()
    return render_template('modifycenter.html', center=center)

@app.route('/center/update/<id>', methods=['GET','POST'])
def update_center_detail(id):
    center_code = request.form['center_code']
    center_name = request.form['center_name']
    db = get_db_connection()
    cur=db.cursor()
    cur.execute("UPDATE centers SET center_code=?, center_name=? WHERE id=?", (center_code,center_name,id,))
    db.commit()
    db.close()
    return redirect(url_for('list_centers'))

@app.route('/center/delete/<id>')
def delete_center(id):
    db = get_db_connection()
    cur=db.cursor()
    cur.execute("DELETE FROM centers WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect(url_for('list_centers'))
def getStudentImageName(id):
    filename=""
    db = get_db_connection()
    cur=db.cursor()
    student=cur.execute("SELECT image_name FROM students WHERE id=?", (id,)).fetchone()
    db.commit()
    db.close()
    if student:
        filename=student['image_name']
    return filename
    
@app.route('/student/delete/<id>')
def delete_student(id):
    image_name = getStudentImageName(id)
    delete_file(os.path.join('images', image_name))
    db = get_db_connection()
    cur=db.cursor()
    cur.execute("DELETE FROM students WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect(url_for('list_students'))
@app.route('/deleteUser/<id>')
def del_user(id):
    db = get_db_connection()
    cur=db.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect(url_for('list_users'))

@app.route('/hallticket/<id>')
def view_hallticket(id):
    image_name=getStudentImageName(id)
    image_name=os.path.join('images', image_name)
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )

    db = get_db_connection()
    student=db.execute("SELECT s.id,s.reg_number,s.student_name,s.center_code,c.center_name,s.verification_code,s.image_name FROM students s inner join centers c on s.center_code=c.center_code WHERE s.id=?", (id,)).fetchone()     
    db.close()
 
    qr.add_data(request.host+'/student/'+id+'/code/'+student['verification_code'])
    #qr.add_data('/student/'+id+'/code/')
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    #img_path = f'images/{id}.jpg'
    #img.save(img_path)

    img_bytes = BytesIO()
    img.save(img_bytes)
    img_bytes.seek(0)  # Move to the start of the BytesIO object

    # Encode the image to base64
    img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
    qr_code_img_data = f"data:image/jpg;base64,{img_base64}" 
    # Open the JPG file
    image_bytes=BytesIO()
    with open(image_name, 'rb') as f:
        # Read the contents of the file
        image_bytes = f.read()
        image_buffer = io.BytesIO()
        image_buffer.write(image_bytes)
        image_buffer.seek(0)
        image_base64 = base64.b64encode(image_buffer.getvalue()).decode('utf-8')
        user_img_data = f"data:image/jpg;base64,{image_base64}"
        

   # x=self.request.host_url
    return render_template('hallticket.html', qr_code_img_data=qr_code_img_data, student=student,user_img_data=user_img_data)
    #return send_file(img_path, mimetype='image/png')

@app.route('/student/<id>/code/<verificationcode>')
def validate_hallticket(id,verificationcode):
    image_name=getStudentImageName(id)
    image_name=os.path.join('images', image_name)
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )

    db = get_db_connection()
    student=db.execute("SELECT s.id,s.reg_number,s.student_name,s.center_code,c.center_name,s.verification_code,s.image_name FROM students s inner join centers c on s.center_code=c.center_code WHERE s.id=?", (id,)).fetchone()     
    db.close()
 
    qr.add_data(request.host+'/student/'+id+'/code/'+student['verification_code'])
    #qr.add_data('/student/'+id+'/code/')
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    #img_path = f'images/{id}.jpg'
    #img.save(img_path)

    img_bytes = BytesIO()
    img.save(img_bytes)
    img_bytes.seek(0)  # Move to the start of the BytesIO object

    # Encode the image to base64
    img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
    qr_code_img_data = f"data:image/jpg;base64,{img_base64}" 
    # Open the JPG file
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
    student=db.execute("SELECT s.id,s.reg_number,s.student_name,s.center_code,c.center_name,s.verification_code FROM students s inner join centers c on s.center_code=c.center_code WHERE s.id=? and s.verification_code=?", (id,verificationcode,)).fetchone()     
    db.close()

    validation_status = {'status': 'failure', 'message': 'Failed'}    
    if student:
        validation_status = {'status': 'success', 'message': 'Valid'}

    else:
        validation_status = {'status': 'failure', 'message': 'Failed'}

    return render_template('hallticketstatus.html', student=student,response_data=validation_status,user_img_data=user_img_data,qr_code_img_data=qr_code_img_data)

if __name__ == '__main__':
    init_db()  # Ensure our database and table are created
    app.run(debug=True)