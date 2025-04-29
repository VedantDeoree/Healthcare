from flask import Flask, render_template, request, redirect, url_for, flash,session,get_flashed_messages
from flask_login import LoginManager, login_user, UserMixin, login_required, logout_user,current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from random import choice
from datetime import timedelta,datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

login_manager = LoginManager()
login_manager.init_app(app)

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Garad@007",
    database="hms"
)
cursor = mydb.cursor()


class User(UserMixin):
    def __init__(self, id,email,name):
        self.id = id
        self.email=email
        self.name=name


@login_manager.user_loader
def load_user(user_id):
        user_type = session.get('user_type')
        if user_type=='patient':
            cursor.execute("SELECT * FROM Patients WHERE PID = %s", (user_id,))
            user_data = cursor.fetchone() 
            if user_data:
              return User(user_data[0],user_data[2],user_data[1])
       
        elif user_type=='doctor':
            cursor.execute("SELECT * FROM Doctors WHERE DID = %s", (user_id,))
            user_data = cursor.fetchone() 
            if user_data:
              return User(user_data[0],user_data[2],user_data[1])
        
        return None

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/patients", methods=["POST", "GET"])
@login_required
def patients():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        gender = request.form.get('gender')
        slot = request.form.get('slot')
        disease = request.form.get('disease')
        booking_date = request.form.get('booking_date')
        booking_time= request.form.get('booking_time')
        doctor_department= request.form.get('department')
        contact_number = request.form.get('contact_number')
        age =request.form.get('age')

        cursor.execute("SELECT * FROM Doctors WHERE Department = %s", (doctor_department,))
        doctors = cursor.fetchall()

        if doctors:
            random_doctor = choice(doctors)
            doctor_name = random_doctor[1]  
        else:
            doctor_name = "No available doctor"
        
        booking_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
        booking_datetime = datetime.combine(booking_date, datetime.strptime(booking_time, "%H:%M").time())
        start_time = booking_datetime - timedelta(hours=1)
        end_time = booking_datetime + timedelta(hours=1)
        print(start_time,end_time)
        print(doctor_name)
        sql = "SELECT COUNT(*) FROM Appointment WHERE DoctorName = %s AND BookingDate = %s AND BookingTime BETWEEN %s AND %s"
        val = (doctor_name,booking_date,start_time,end_time)
        cursor.execute(sql, val)
        existent = cursor.fetchall()
        print(existent)
        
        if existent[0][0] == 0:
            sql = "SELECT COUNT(*) FROM Appointment WHERE DoctorName = %s"
            val = (doctor_name,)
            cursor.execute(sql,val)
            existent1 = cursor.fetchall()
            if existent1[0][0] > 8 :
                render_template("message.html")
            else:
                sql = "INSERT INTO Appointment (Email, Name, Gender, Slot, Disease, BookingDate, BookingTime, DoctorDepartment, DoctorName, PhoneNumber, Age) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (email, name, gender, slot, disease, booking_date, booking_time, doctor_department, doctor_name, contact_number, age)
                cursor.execute(sql, val)
                mydb.commit()
                flash("Appointment Successful!", "info")
                
        else:
            render_template("message1.html")
            
    return render_template("patients.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
    
        sql = "SELECT * FROM Patients WHERE Email = %s"
        val = (email,)
        cursor.execute(sql, val)
        existing_patient = cursor.fetchone()

        if existing_patient:
            flash("User exists please login!", "error")
            return render_template("signup.html")


        else:
            hashed_password = generate_password_hash(password)
            sql = "INSERT INTO Patients (Username, Email, Password) VALUES (%s, %s, %s)"
            val = (username, email, hashed_password)
            cursor.execute(sql, val)
            mydb.commit()
            return redirect(url_for('login'))

    return render_template("signup.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        typeofuser=request.form.get('typeofuser')

        if typeofuser=='Doctor':
                 session['user_type'] = 'doctor'
                 sql = "SELECT * FROM Doctors WHERE Email = %s"
                 val = (email,)
                 cursor.execute(sql, val)
                 existing_doctor = cursor.fetchone()

                 if existing_doctor:
                   if check_password_hash(existing_doctor[3], password):
                      user = User(existing_doctor[0],existing_doctor[2],existing_doctor[1])
                      login_user(user)
                      flash("Login successful", 'success')
                      app.logger.debug(get_flashed_messages())
                      return redirect(url_for('doctorshome')) 
                   else:
                      flash("Invalid password",'error')
                      return render_template("login.html")
                 else:
                   flash("Invalid email", "error")
                   return render_template("login.html")
           
        elif typeofuser=='Patient': 
            session['user_type'] = 'patient'   
            sql = "SELECT * FROM Patients WHERE Email = %s"
            val = (email,)
            cursor.execute(sql, val)
            existing_patient = cursor.fetchone()

            
            if existing_patient and check_password_hash(existing_patient[3], password):
                    user = User(existing_patient[0],existing_patient[2],existing_patient[1])
                    login_user(user)
                    return redirect(url_for('patients'))                
            else:
                    flash("Invalid Credentials",'error')
                    return render_template("login.html")
            
        
        else:
            flash("Invalid Type of User", "error")
            return render_template("login.html")

    return render_template("login.html")


@app.route("/appointmentdetails",methods=["POST","GET"])
@login_required
def appointmentdetails():
    if request.method == "GET":
        cursor.execute("SELECT * FROM Appointment WHERE Email = %s", (current_user.email,))
        booking_data = cursor.fetchall()
        return render_template("appointmentdetails.html", bookings=booking_data)


@app.route("/delete/<int:AID>",methods=["POST","GET"])
@login_required
def delete(AID):
    cursor.execute("DELETE FROM Appointment WHERE AID = %s", (AID,))
    mydb.commit()
    flash("Booking record deleted successfully", "success")
    return redirect(url_for("appointmentdetails"))


@app.route("/edit/<string:AID>",methods=["POST","GET"])
@login_required
def edit(AID):
    cursor.execute("SELECT * FROM Appointment WHERE AID = %s", (AID,))
    user_data = cursor.fetchone() 
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        gender =request.form.get('gender')
        slot =request.form.get('slot')
        disease =request.form.get('disease')
        booking_date =request.form.get('booking_date')
        booking_time=request.form.get('booking_time')
        doctor_department=request.form.get('department')
        contact_number =request.form.get('contact_number')
        age =request.form.get('age')

        cursor.execute("SELECT * FROM Doctors WHERE Department = %s", (doctor_department,))
        doctors = cursor.fetchall()

        if doctors:
            random_doctor = choice(doctors)
            doctor_name = random_doctor[1]  
        else:
            doctor_name = "No available doctor"

        booking_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
        booking_datetime = datetime.combine(booking_date, datetime.strptime(booking_time, "%H:%M").time())
        start_time = booking_datetime - timedelta(hours=1)
        end_time = booking_datetime + timedelta(hours=1)
        print(start_time,end_time)
        print(doctor_name)
        sql = "SELECT COUNT(*) FROM Appointment WHERE DoctorName = %s AND BookingDate = %s AND BookingTime BETWEEN %s AND %s"
        val = (doctor_name,booking_date,start_time,end_time)
        cursor.execute(sql, val)
        existent = cursor.fetchall()
        print(existent)

        if existent[0][0] == 0:
            sql = "SELECT COUNT(*) FROM Appointment WHERE DoctorName = %s"
            val = (doctor_name,)
            cursor.execute(sql,val)
            existent1 = cursor.fetchall()
            if existent1[0][0] > 8 :
                render_template("message.html")
            else:
                sql = "UPDATE Appointment SET Email = %s, Name = %s, Gender = %s, Slot = %s, Disease = %s, BookingDate = %s, BookingTime = %s, DoctorDepartment = %s, DoctorName = %s, PhoneNumber = %s, Age = %s WHERE AID = %s"
                val = (email, name, gender, slot, disease, booking_date, booking_time, doctor_department, doctor_name, contact_number, age, AID)
                cursor.execute(sql, val)
                mydb.commit()
                flash("Appointment Successful!", "info")
                return redirect(url_for('appointmentdetails'))
        else:
            render_template("message1.html")
        
    return render_template("edit.html",query=user_data)


@app.route("/doctors", methods=["GET"])
@login_required
def doctors():
    if request.method == "GET":
        cursor.execute("SELECT DID, Name, Email, Password, Department, ContactNumber, Qualification FROM Doctors ORDER BY department")
        doctor_data = cursor.fetchall()
        return render_template("doctors.html", doctors=doctor_data)
    

@app.route("/doctorshome")
@login_required
def doctorshome():
    return render_template("doctorshome.html")


@app.route("/doctor")
@login_required
def doctor():
   if request.method == "GET":
        cursor.execute("SELECT DID, Name, Email, Password, Department, ContactNumber, Qualification FROM Doctors ORDER BY department")
        doctor_data = cursor.fetchall()
        return render_template("doctor.html", doctor=doctor_data)


@app.route("/doctorspro",methods=["GET","POST"])
@login_required
def doctorspro():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        password =request.form.get('password')
        department =request.form.get('department')
        contact =request.form.get('contact_number')
        qualification =request.form.get('qualification')  

        sql = "SELECT * FROM Doctors WHERE Email = %s"
        val = (email,)
        cursor.execute(sql, val)
        existing_patient = cursor.fetchone()

        if existing_patient:
            flash("Doctor exists please add new!", "error")
            return render_template("doctorpro.html")


        else:
            hashed_password = generate_password_hash(password)
            sql = "INSERT INTO Doctors (Name, Email, Password, Department,ContactNumber, Qualification ) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (name, email, hashed_password,department,contact,qualification)
            cursor.execute(sql, val)
            mydb.commit()
            flash("Doctor Added!", "success")
    return render_template("doctorpro.html")


@app.route("/bookings", methods=["GET", "POST"])
@login_required
def booking():
    if request.method == "GET":
        return render_template("bookings.html")

@app.route("/overallbooking", methods=["GET"])
@login_required
def overallbooking():
    if request.method == "GET":
        cursor.execute("SELECT * FROM Appointment")
        bookings = cursor.fetchall()
        return render_template("overall.html", booking=bookings)


@app.route("/personalbooking", methods=["GET"])
@login_required
def personalbooking():
    if request.method == "GET":
        current_doctor_name = current_user.name
        cursor.execute("SELECT * FROM Appointment WHERE DoctorName = %s", (current_doctor_name,))
        bookings = cursor.fetchall()
        return render_template("personal.html", book=bookings)
    
@app.route("/search", methods=["GET","POST"])
@login_required
def search():
    if request.method == "POST":
        P_ID = request.form.get("PID")
        print(P_ID)
        cursor.execute("SELECT * FROM Patients WHERE PID = %s", (P_ID,))
        existent2 = cursor.fetchone()
        if existent2 is not None:
            abc = existent2[2]
            cursor.execute("SELECT * FROM Appointment WHERE Email = %s", (abc,))
            existent3 = cursor.fetchall()
            return render_template("search.html", xyz=existent3)
        else:
            return render_template("bookings.html")
    return render_template("bookings.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for("login"))



app.run(debug=True)
