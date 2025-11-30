from flask import Flask, render_template, request, send_file, redirect ,url_for,session,jsonify,flash
import sqlite3
import os
from io import BytesIO
import base64
import hashlib,logging,sys
import io
from datetime import datetime, time
import random

app = Flask(__name__)
app.secret_key = '457884758745jhertjjhert874957ejthdnflnsdflnsdk;fjhsdfh'
DATABASE = 'rmos.db'

cart = []
cartSummary = []
global orderid
global OTP

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
def string_to_time(time_str):
    try:
        # Parse the time string using strptime
        time_object = datetime.strptime(time_str, '%H:%M:%S').time()
        return time_object
    except ValueError:
        # Handle the case where the input string is not in the expected format
        print("Invalid time format. Please provide time in HH:MM:SS format.")
        return None

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
            return 'Invalid username or password'
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

@app.route('/user/add', methods=['GET','POST'])
def add_user():
    user_id = request.form['userid']
    user_name = request.form['username']
    user_email = request.form['email']
    user_password = request.form['password']
    create_user(user_id,user_name,user_email,user_password)
    flash("User has been created successfully",'success')
    return redirect(url_for('list_users'))

@app.route('/deleteUser/<id>')
def del_user(id):
    db = get_db_connection()
    cur=db.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect(url_for('list_users'))

@app.route('/timeslots')
def list_timeslots():
    if 'logged_in' not in session:
        return render_template('loginForm.html')
    db = get_db_connection()
    result_data = db.execute('SELECT * FROM timeslots').fetchall()
    db.close()
    return render_template('timeslot/timeslots.html', timeslots=result_data)

@app.route('/timeslot/new')
def open_new_timeslot():
    if 'logged_in' not in session:
        return render_template('loginForm.html')
    return render_template('timeslot/newtimeslot.html')

@app.route('/timeslot/add', methods=['GET','POST'])
def add_timeslot():
    time_code = request.form['time_code']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    time_code = time_code.upper()
    if isDataPresent('timeslots','time_code',time_code):
        flash('Timeslot code already present','error')
        return redirect(url_for('open_new_timeslot'))
    db = get_db_connection()
    db.execute('INSERT INTO timeslots (time_code,start_time,end_time) VALUES (?, ?, ?)', (time_code,start_time,end_time))
    db.commit()
    db.close()
    return redirect(url_for('list_timeslots'))

@app.route('/timeslot/delete/<id>')
def delete_timeslot(id):
    db = get_db_connection()
    cur=db.cursor()
    cur.execute("DELETE FROM timeslots WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect(url_for('list_timeslots'))


@app.route('/timeslot/edit/<id>')
def open_edit_department(id):
    db = get_db_connection()
    cur=db.cursor()
    result_data=cur.execute("SELECT * FROM timeslots WHERE id=?", (id,)).fetchone()
    db.commit()
    db.close()
    return render_template('timeslot/edittimeslot.html', timeslot=result_data)

@app.route('/timeslot/update/<id>', methods=['GET','POST'])
def update_timeslot(id):
    try:
        time_code = request.form['time_code']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        time_code = time_code.upper()
        db = get_db_connection()
        cur=db.cursor()
        cur.execute("UPDATE timeslots SET start_time=?, end_time=? WHERE id=?", (start_time,end_time,id,))
        db.commit()
        db.close()
        flash('Record updated successfully!','success')
    except Exception as e:
            flash('Error Occurred','danger')
    finally:
        return redirect(url_for('list_timeslots'))
    
@app.route('/menus')
def list_menus():
    if 'logged_in' not in session:
        return render_template('loginForm.html')
    db = get_db_connection()
    result_data = db.execute('SELECT * FROM menus').fetchall()
    db.close()
    return render_template('menu/menus.html', menus=result_data)

def getMenuListForOrder():
    db = get_db_connection()
    currenttime=datetime.now().strftime("%H:%M:%S")
    currenttime=str(currenttime)
    strquery="""SELECT m.menu_code,m.menu_name,m.menu_price,m.menu_description 
    FROM menus m inner join menutime t on m.menu_code = t.menu_code 
    inner join timeslots s on t.time_code=s.time_code where '""" + currenttime + """' between time(s.start_time) and time(s.end_time)
            """
    result_data = db.execute(strquery).fetchall()
    db.close()
    return result_data
@app.route('/menu/list')
def list_menus_for_order():
    result_data =getMenuListForOrder()
    global cart
    global cartSummary
    return render_template('order/menulistfororder.html', menus=result_data, cart=cart, cartSummary=cartSummary)

def find_item(name):
    for i, item in enumerate(cart):
        if item['menu_code'] == name:
            return i
    return None

def getCartSummary(cart):
    totalQuantity = 0
    totalAmount=0
    global cartSummary
    for i,item in enumerate(cart):
        totalQuantity += item['quantity'] 
        totalAmount += item['total'] 
    cartSummary.clear()
    cartSummary.append({'t_quantity': totalQuantity, 't_price': totalAmount})
    return cartSummary

@app.route('/order/<menu_code>', methods=['GET','POST'])
def add_to_cart(menu_code):
    db = get_db_connection()
    cur=db.cursor()
    menudata=cur.execute("SELECT * FROM menus WHERE menu_code=?", (menu_code,)).fetchone()
    db.commit()
    db.close()
    global cart
    global cartSummary
    if menudata:
        menu_code = menudata['menu_code']
        menu_name = menudata['menu_name']
        quantity = 1
        unit_price = float(menudata['menu_price'])
        total = quantity * unit_price
        index = find_item(menu_code)
        if index is not None:
            cart[index]['quantity'] += quantity
            cart[index]['total'] += total
        else:            
            cart.append({'menu_code': menu_code, 'menu_name': menu_name, 'quantity': quantity, 'unit_price': unit_price, 'total': total})
    result_data =getMenuListForOrder()
    cartSummary = getCartSummary(cart)
    return render_template('order/menulistfororder.html', menus=result_data,cart=cart,cartsummary=cartSummary)

@app.route('/ordersummary/addquantity/<menu_code>', methods=['GET','POST'])
def add_order_quantity(menu_code):
    db = get_db_connection()
    cur=db.cursor()
    menudata=cur.execute("SELECT * FROM menus WHERE menu_code=?", (menu_code,)).fetchone()
    db.commit()
    db.close()
    global cart
    global cartSummary
    if menudata:
        quantity=1
        menu_code = menudata['menu_code']
        menu_name = menudata['menu_name']
        unit_price = float(menudata['menu_price'])
        total = quantity * unit_price
        index = find_item(menu_code)
        if index is not None:
            cart[index]['quantity'] += quantity
            cart[index]['total'] += total
        else:            
            cart.append({'menu_code': menu_code, 'menu_name': menu_name, 'quantity': quantity, 'unit_price': unit_price, 'total': total})
       
    cartSummary = getCartSummary(cart)    
    return render_template('order/ordersummary.html',cart=cart,cartSummary=cartSummary)

def getOrderID():
    return datetime.now().strftime("%Y%m%d%H%M%S%f")

def getOTP():
    return ''.join(random.choices('0123456789', k=6))

@app.route('/order/search', methods=['GET','POST'])
def open_search_order():
    return render_template('order/yourorderdetail.html')


@app.route('/order/find', methods=['GET','POST'])
def search_order():
    reference_number = request.form['reference_number']
    sqlQuery ="""Select o.order_id,m.menu_name,m.menu_price, d.quantity, m.menu_price*d.quantity as t_price from menuorder o inner join oderdetail d on d.order_id=o.order_id
            inner join menus m on m.menu_code = d.menu_code
            where o.order_token=?
            """
    db = get_db_connection()    
    result_data=db.execute(sqlQuery, (reference_number,)).fetchall()
    db.close()
    totalprice=0
    totalquantity=0
    orderid=""
    if result_data:
        for item in result_data:
            orderid = item['order_id']
            totalprice += item['t_price']
            totalquantity += item['quantity']        
        return render_template('order/yourorderdetail.html',orderid=orderid,oderdetails=result_data, totalprice=totalprice, totalquantity=totalquantity)    
    flash("Invalid Reference number",'danger')
    return render_template('order/yourorderdetail.html')

@app.route('/order/create', methods=['GET','POST'])
def submit_order():
    global cart
    global orderid
    global OTP
    orderid=getOrderID()
    OTP=getOTP()
    if cart:
        if len(cart) > 0:            
            curdate=str(datetime.now())
            db = get_db_connection()            
            db.execute('INSERT INTO menuorder (order_id, order_token, order_date) VALUES (?, ?, ?)', (orderid, OTP,curdate))            
            for item in cart:
                db.execute('INSERT INTO oderdetail (order_id, menu_code, quantity) VALUES (?, ?, ?)', (orderid, item['menu_code'],item['quantity']))
            db.commit()
            db.close()
            cart.clear()
            return render_template('order/ordersuccess.html',orderid=orderid, OTP=OTP)
    flash("Error occurred while placing order, Please submit again",'danger')
    return redirect(url_for('list_menus_for_order'))
    


@app.route('/ordersummary/lessquantity/<menu_code>', methods=['GET','POST'])
def less_order_quantity(menu_code):
    db = get_db_connection()
    cur=db.cursor()
    menudata=cur.execute("SELECT * FROM menus WHERE menu_code=?", (menu_code,)).fetchone()
    db.commit()
    db.close()
    global cart
    if menudata:
        quantity=1
        menu_code = menudata['menu_code']
        menu_name = menudata['menu_name']
        unit_price = float(menudata['menu_price'])
        total = quantity * unit_price
        index = find_item(menu_code)
        if index is not None: 
            if cart[index]['quantity'] > 0 :
                cart[index]['quantity'] -= quantity
                cart[index]['total'] -= total
            else:
                del cart[index]
        else:            
            cart.append({'menu_code': menu_code, 'menu_name': menu_name, 'quantity': quantity, 'unit_price': unit_price, 'total': total})
    cartSummary = getCartSummary(cart)
    return render_template('order/ordersummary.html',cart=cart, cartSummary=cartSummary)

@app.route('/menu/new')
def open_new_menu():
    if 'logged_in' not in session:
        return render_template('loginForm.html')
    return render_template('menu/newmenu.html')

@app.route('/order/summary')
def open_odrer_summary():
    global cart
    return render_template('order/ordersummary.html',cart=cart,cartSummary=cartSummary)

@app.route('/menu/add', methods=['GET','POST'])
def add_menu():
    try:
        menu_code = request.form['menu_code'].upper()
        menu_name = request.form['menu_name']
        menu_price = request.form['menu_price']
        menu_description = request.form['menu_description']     
        menu_price = round(float(menu_price),2)
        if isDataPresent('menus','menu_code',menu_code):
            flash('Menu code already present','error')
            return redirect(url_for('open_new_menu'))
        db = get_db_connection()
        last_record_id=db.execute('INSERT INTO menus (menu_code, menu_name, menu_price,menu_description) VALUES (?, ?, ?, ?)', (menu_code, menu_name,menu_price,menu_description)).lastrowid
        db.commit()
        db.close()       
        flash('Menu created sucessfully!','success')
    except Exception as e:
        flash(f"An error occurred: {str(e)}",'danger')
        
    finally:          
        return redirect(url_for('list_menus'))
    
@app.route('/menu/view/<id>', methods=['GET','POST'])
def open_view_menu(id):
    db = get_db_connection()
    cur=db.cursor()
    result_data=cur.execute("SELECT * FROM menus WHERE id=?", (id,)).fetchone()
    db.commit()
    db.close()
    
    if result_data:
        db = get_db_connection()
        cur=db.cursor()
        result_data_time=cur.execute("SELECT t.time_code,t.start_time,t.end_time FROM menutime m inner join timeslots t on m.time_code=t.time_code WHERE m.menu_code=?", (result_data['menu_code'],)).fetchall()
        db.commit()
        db.close()
    db = get_db_connection()
    cur=db.cursor()
    result_data_slots = db.execute('SELECT * FROM timeslots').fetchall()
    db.commit()
    db.close()
    return render_template('menu/viewmenu.html', menu=result_data,menutimes=result_data_time,timeslots=result_data_slots)

def open_view_menubyCode(menu_code):
    db = get_db_connection()
    cur=db.cursor()
    result_data=cur.execute("SELECT * FROM menus WHERE menu_code=?", (menu_code,)).fetchone()
    db.commit()
    db.close()
    
    if result_data:
        db = get_db_connection()
        cur=db.cursor()
        result_data_time=cur.execute("SELECT t.time_code,t.start_time,t.end_time FROM menutime m inner join timeslots t on m.time_code=t.time_code WHERE m.menu_code=?", (result_data['menu_code'],)).fetchall()
        db.commit()
        db.close()
    db = get_db_connection()
    cur=db.cursor()
    result_data_slots = db.execute('SELECT * FROM timeslots').fetchall()
    db.commit()
    db.close()
    return render_template('menu/viewmenu.html', menu=result_data,menutimes=result_data_time,timeslots=result_data_slots)

@app.route('/menu/edit/<id>', methods=['GET','POST'])
def open_edit_menu(id):
    db = get_db_connection()
    cur=db.cursor()
    result_data=cur.execute("SELECT * FROM menus WHERE id=?", (id,)).fetchone()
    db.commit()
    db.close()
    return render_template('menu/editmenu.html', menu=result_data)

@app.route('/menu/update/<id>', methods=['GET','POST'])
def update_menu(id):
    try:
        menu_code = request.form['menu_code'].upper()
        menu_name = request.form['menu_name']
        menu_price = request.form['menu_price']
        menu_description = request.form['menu_description']  
        menu_price = round(float(menu_price),2)
        
        db = get_db_connection()
        db.execute('update menus set menu_code=?, menu_name=?,menu_price=?,menu_description=? WHERE id=?', (menu_code, menu_name,menu_price,menu_description,id,))
        db.commit()
        db.close()
        
        flash('Menu updated sucessfully!','success')
    except Exception as e:
        flash(f"An error occurred: {str(e)}",'danger')        
    finally:          
        return redirect(url_for('list_menus'))

@app.route('/menu/availability/add/<menu_code>', methods=['GET','POST'])
def add_menu_availability(menu_code):
    try:
        menu_code = menu_code
        time_code = request.form['menu_timeslot']
        
        db = get_db_connection()
        last_record_id=db.execute('INSERT INTO menutime (menu_code, time_code) VALUES (?, ?)', (menu_code, time_code)).lastrowid
        db.commit()
        db.close()
        flash('Menu availability added sucessfully!','success')
    except Exception as e:
        flash(f"An error occurred: {str(e)}",'danger')        
    finally:
        return open_view_menubyCode(menu_code)

@app.route('/menu/delete/<id>')
def delete_menu(id):
    
    try:
        db = get_db_connection()
        cur=db.cursor()
        cur.execute("DELETE FROM menus WHERE id=?", (id,))
        db.commit()
        db.close()
        flash('Record Deleted successfully','success')
    except Exception as e:
        flash(f"An error occurred: {str(e)}",'danger')
        
    finally:          
        return redirect(url_for('list_menus'))

@app.route('/menu/<menu_code>/availability/delete/<time_code>')
def delete_menu_availability(menu_code,time_code):
    
    try:
        db = get_db_connection()
        cur=db.cursor()
        cur.execute("DELETE FROM menutime WHERE menu_code=? and time_code=?", (menu_code,time_code,))
        db.commit()
        db.close()
        flash('Record Deleted successfully','success')
    except Exception as e:
        flash(f"An error occurred: {str(e)}",'danger')
        
    finally:          
        return open_view_menubyCode(menu_code)



@app.template_filter('format_decimal')
def format_decimal(value):
    return '{:.2f}'.format(value)

if __name__ == '__main__':
    init_db()  # Ensure our database and table are created
    app.run(debug=True)