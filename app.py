from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "medtracksecret"


def get_db():
    conn = sqlite3.connect("medtrack.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return render_template("index.html")


# ---------------- PATIENT REGISTER ----------------

@app.route("/patient_register", methods=["GET","POST"])
def patient_register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        conn.execute("INSERT INTO patients (name,email,password) VALUES (?,?,?)",
                     (name,email,password))
        conn.commit()
        conn.close()

        return redirect("/patient_login")

    return render_template("patient_register.html")


# ---------------- PATIENT LOGIN ----------------

@app.route("/patient_login", methods=["GET","POST"])
def patient_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM patients WHERE email=? AND password=?",
                            (email,password)).fetchone()

        conn.close()

        if user:
            session["patient"] = user["id"]
            return redirect("/patient_dashboard")
        else:
            return "Invalid Credentials"

    return render_template("patient_login.html")


# ---------------- DOCTOR REGISTER ----------------

@app.route("/doctor_register", methods=["GET","POST"])
def doctor_register():

    if request.method == "POST":

        name = request.form["name"]
        speciality = request.form["speciality"]
        email = request.form["email"]
        password = request.form["password"]
        timing = request.form["timing"]
        days = request.form["days"]

        conn = get_db()

        conn.execute(
        "INSERT INTO doctors (name,speciality,email,password,timing,days) VALUES (?,?,?,?,?,?)",
        (name,speciality,email,password,timing,days)
        )

        conn.commit()
        conn.close()

        return redirect("/doctor_login")

    return render_template("doctor_register.html")


# ---------------- DOCTOR LOGIN ----------------

@app.route("/doctor_login", methods=["GET","POST"])
def doctor_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        doctor = conn.execute(
            "SELECT * FROM doctors WHERE email=? AND password=?",
            (email,password)
        ).fetchone()

        conn.close()

        if doctor:
            session["doctor"] = doctor["id"]
            return redirect("/doctor_dashboard")

        else:
            return "Invalid Credentials"

    return render_template("doctor_login.html")


# ---------------- PATIENT DASHBOARD ----------------

@app.route("/patient_dashboard", methods=["GET","POST"])
def patient_dashboard():

    conn = get_db()
    doctors = conn.execute("SELECT * FROM doctors").fetchall()

    booked = False

    if request.method == "POST":

        doctor_id = request.form["doctor"]
        date = request.form["date"]
        time = request.form["time"]
        reason = request.form["reason"]

        doctor = conn.execute(
        "SELECT timing,days FROM doctors WHERE id=?",
        (doctor_id,)
        ).fetchone()

        # simple availability check
        if doctor:

            conn.execute(
            "INSERT INTO appointments (patient_id,doctor_id,date,time,reason) VALUES (?,?,?,?,?)",
            (session["patient"],doctor_id,date,time,reason)
            )

            conn.commit()
            booked = True

    conn.close()

    return render_template("patient_dashboard.html", doctors=doctors, booked=booked)

# ---------------- DOCTOR DASHBOARD ----------------

@app.route("/doctor_dashboard")
def doctor_dashboard():

    conn = get_db()

    appointments = conn.execute("""
    SELECT appointments.date, appointments.time, appointments.reason, patients.name
    FROM appointments
    JOIN patients ON appointments.patient_id = patients.id
    WHERE doctor_id = ?
    """,(session["doctor"],)).fetchall()

    conn.close()

    return render_template("doctor_dashboard.html",appointments=appointments)

@app.route('/appointments')
def view_appointments():
    conn = get_db()

    # Check if logged in user is a patient or doctor
    if 'patient' in session:
        user_id = session['patient']
        # Get patient appointments with doctor details
        appointments = conn.execute("""
            SELECT appointments.date, doctors.name AS doctor_name, doctors.speciality
            FROM appointments
            JOIN doctors ON appointments.doctor_id = doctors.id
            WHERE appointments.patient_id = ?
            ORDER BY appointments.date DESC
        """, (user_id,)).fetchall()

    elif 'doctor' in session:
        user_id = session['doctor']
        # Get doctor appointments with patient details
        appointments = conn.execute("""
            SELECT appointments.date, patients.name AS patient_name
            FROM appointments
            JOIN patients ON appointments.patient_id = patients.id
            WHERE appointments.doctor_id = ?
            ORDER BY appointments.date DESC
        """, (user_id,)).fetchall()
    else:
        # Not logged in
        return redirect('/')

    conn.close()

    return render_template('appointments.html', appointments=appointments)

@app.route("/logout")
def logout():
    session.clear()   # removes patient or doctor session
    return redirect("/")   # redirect to index page

if __name__ == "__main__":
    app.run(debug=True)

