from flask import Flask, render_template, request, redirect,url_for
import mysql.connector
app = Flask(__name__)

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Gayathri@12345',
        database='flask'
    )
    cursor = conn.cursor()
except mysql.connector.Error as e:
    print("Error connecting to MySQL database:", e)


# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for the about page
@app.route('/about')
def about():
    return render_template('about.html')

# Route for the services page
@app.route('/services')
def services():
    return render_template('services.html')

# Route for the doctors page
@app.route('/doctors')
def doctors():
    return render_template('doctors.html')

# Route for the contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Route for handling form submission
@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST' :
            Firstname = request.form['Firstname']
            Lastname = request.form['Lastname']
            Email = request.form['Email']                
            Mobile = request.form['mob']
            sex=request.form['sex']
            AppointmentDate=request.form['AppointmentDate']
            Additional_information=request.form['Additional_information']
            
            try:
                cursor.execute("INSERT INTO appointments (Firstname, Lastname,email,mobile,sex,AppointmentDate,Additional_information) VALUES (%s,%s, %s, %s, %s, %s,%s)", 
                                   (Firstname, Lastname,Email,Mobile,sex,AppointmentDate,Additional_information))
                conn.commit()
                return redirect(url_for('appointment'))
            except mysql.connector.Error as e:
                print("Error executing SQL query:", e)
            return redirect(url_for('appointment'))
    else:
        pass

# Route for the appointment page
@app.route('/appointment')
def appointment():
        cursor.execute("SELECT * FROM appointments")
        value = cursor.fetchall()
        print("Appointment", value)
        return render_template('appointment.html',data=value)
@app.route('/update/<patient_id>')
def update(patient_id):
    cursor.execute("SELECT * FROM appointments WHERE patient_id = %s", (patient_id,))
    value = cursor.fetchone()
    return render_template('update.html', data=value)

@app.route('/edit_note', methods=['POST', 'GET'])
def edit_note():
    if request.method == 'POST':
        try:
            patient_id = request.form['patient_id']
            Firstname = request.form['Firstname']
            Lastname = request.form['Lastname']
            Email = request.form['Email']                
            Mobile = request.form['mob']
            sex = request.form['sex']
            AppointmentDate = request.form['AppointmentDate']
            Additional_information = request.form['Additional_information']
            
            update_query = "UPDATE appointments SET Firstname=%s, Lastname=%s, Email=%s, Mobile=%s, sex=%s, AppointmentDate=%s, Additional_information=%s WHERE patient_id=%s"
            cursor.execute(update_query, (Firstname, Lastname, Email, Mobile, sex, AppointmentDate, Additional_information, patient_id))
            conn.commit()
            
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
        
        return redirect(url_for('appointment'))
    
    else:
        pass

@app.route('/delete/<patient_id>')
def delete(patient_id):
    try:
        cursor.execute("DELETE FROM appointments WHERE patient_id= %s", (patient_id,))
        conn.commit()
    except mysql.connector.Error as e:
        print("Error executing SQL query:", e)

    return redirect(url_for('appointment'))

if __name__ == '__main__':
    app.run(debug=True)
