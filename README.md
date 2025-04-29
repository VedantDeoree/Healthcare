# Hospital Management System (HMS) - Flask Web App

A web-based Hospital Management System built using Python (Flask), MySQL, and HTML/CSS. The system allows **Patients** to book appointments and **Doctors** to manage appointments efficiently.

## 🛠 Features

- Secure Patient & Doctor authentication using Flask-Login.
- Patient appointment booking with:
  - Time conflict checks
  - Doctor availability constraints
- Doctor profile management and viewing assigned appointments.
- Edit and delete appointments functionality.
- Passwords are securely hashed using Werkzeug.
- Flash messages for interactive user feedback.
- Session management using Flask sessions.

## 🚀 Technologies Used

- **Backend:** Python, Flask, Flask-Login
- **Frontend:** HTML, Jinja2 templates
- **Database:** MySQL
- **Security:** Password hashing with Werkzeug
- **Session Management:** Flask `session`

## 📁 Directory Structure

```bash
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── signup.html
│   ├── patients.html
│   ├── doctors.html
│   ├── doctor.html
│   ├── doctorshome.html
│   ├── appointmentdetails.html
│   ├── edit.html
│   ├── message.html
│   └── message1.html
├── static/
│   └── (CSS, JS, images if any)
├── app.py
└── README.md
