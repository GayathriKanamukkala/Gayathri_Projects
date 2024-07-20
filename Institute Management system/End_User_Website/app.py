from flask import Flask, render_template,request,redirect,url_for
import mysql.connector
app=Flask(__name__)
try:
  connection = mysql.connector.connect(
        host='localhost',
        user="root",
        password='Avanthi@8870',
        database='course_management'
    )   
  Cursor=connection.cursor()
except mysql.connector.Error as e:
    print('Error connectinng to MYSQL:',e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/courses')
def courses():
    # Cursor=connection.cursor(dictionary=True)
    try:
                Cursor.execute("select * from courses")
                value = Cursor.fetchall()
                return render_template('courses.html',courses=value)
    except mysql.connector.Error as e:
       print("system error",e)
       return"Error fetching data from the database"
@app.route('/course_details/<int:course_id>', methods=['GET', 'POST'])
def course_details(course_id):

    print(course_id)
    Cursor=connection.cursor(dictionary=True)
    Cursor.execute('SELECT * FROM courses WHERE course_id = %s', (course_id,))
    course = Cursor.fetchone()
    
    Cursor.execute('SELECT * FROM topics WHERE course_id = %s', (course_id,))
    topics = Cursor.fetchall()
    #   print("topics: ",topics[0][1])
    for topic in topics:
        #   print("SSSSSSS: ",topic['topic_id'])
          Cursor.execute('SELECT * FROM subtopics WHERE topic_id = %s', (topic['topic_id'],))
          topic['sub_topics'] = Cursor.fetchall()
    
        #   connection.close()
    return render_template('course_details.html', course=course,topics=topics)

    
    #   return render_template('course_details.html')
# @app.route('/course_details/<course_id>',methods=['GET','POST'])
# def course_details(course_id):
#       return render_template('course_details.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/ourTeam')
def ourTeam():
  try:
                Cursor.execute("SELECT Faculty_id, Faculty_name, Faculty_description, photo FROM Faculty")
                faculty = Cursor.fetchall()
                return render_template('ourTeam.html',faculty=faculty)
  except mysql.connector.Error as e:
       print("system error",e)
       return"Error fetching data from the database"
@app.route('/contactUs')
def contactUs():
    return render_template('contactUs.html')

@app.route('/display',methods=['POST','GET'])
def display():
    msg=""
    if request.method=='POST':  
        name=request.form['name']
        email=request.form['email']
        phone=request.form['phone']
        Message=request.form[' Message']
        try:
          Cursor.execute("INSERT INTO stu_details(name,email,phone,Message) VALUES (%s, %s,%s,%s)", (name,email,phone,Message))
          connection.commit()
          msg = 'Your Massage has been sent  successfully!'
        except mysql.connector.Error as er:
          print('system error',er)
        return render_template('contactUs.html',msg=msg)
    else:
       pass

@app.route("/dashboard")
def dashboard():
   try:
      Cursor.execute("select * from stu_details")
      value = Cursor.fetchall()
      return render_template('dashboard.html',data=value)
   except mysql.connector.Error as e:
      print("system error",e)
      return"Error fetching data from the database"
@app.route('/update/<id>')
def update(id):
    Cursor.execute('SELECT * FROM stu_details WHERE id = %s', (id,))
    value = Cursor.fetchone()
    return render_template('edit.html', data=value)

@app.route('/delete/<id>')
def delete(id):
    try:
        Cursor.execute('DELETE FROM stu_details WHERE id = %s', (id,))
        return redirect(url_for('dashboard'))
    except mysql.connector.Error as e:
      print("system error",e)
      return"Error fetching data from the database"
@app.route('/edit_section', methods=['POST', 'GET'])
def edit_section():
    if request.method == 'POST':
        try:
            id=request.form['id']
            fname=request.form['fname']
            lname=request.form['lname']
            email=request.form['email']
            course=request.form['course']
            subject=request.form['subject']
            Cursor.execute(
                    "UPDATE stu_details SET fname = %s, lname = %s, email = %s, course = %s, subject = %s WHERE id = %s",
                    (fname, lname, email, course, subject, id)
                )
            connection.commit()
            return redirect(url_for('dashboard'))
        except mysql.connector.Error as er:
            print('System error:', er)
            return "Database error during update"
    else:
        return "Invalid request method"
    
@app.route('/enrollment_form', methods=['POST', 'GET'])
def enrollment_form():
    if request.method == 'POST':
        # Assuming course_id and course_name are passed from a form
        course_id = request.form['course_id']
        course_name = request.form['course_name']
        return render_template('enrollment_form.html', course_name=course_name, course_id=course_id)
    
    # # Handle GET request if any
    return render_template('enrollment_form.html')

# Route for handling form submission and database insertion
@app.route('/enroll', methods=['POST', 'GET'])
def enroll():
    msg = ''
    print("QQQQ: ",request.method)
    #if request.method == 'POST':
    print("hi")
    course_id = request.form['course_id']
    print("course_id: ",course_id)
    name = request.form['name']
    email = request.form['email']
    mobile = request.form['mobile']
    message = request.form['message']
    print("course_id: ",course_id)
    try:
        # Inserting data into the database
        Cursor.execute("INSERT INTO enroll_info (course_id,name, email, mobile, message) VALUES (%s, %s, %s, %s,%s)", (course_id,name, email, mobile, message))
        connection.commit()
        msg = 'You have been enrolled successfully!'
    except mysql.connector.Error as er:
        print('System error:', er)
        msg = 'Error occurred during enrollment'
        # return render_template('enrollment_form.html', msg=msg)

    # After insertion, render the form page again with the message
    print("gggg:",msg)
    return render_template('enrollment_form.html', msg=msg)

    # Handle GET request if any
    #return render_template('enrollment_form.html')

@app.route("/dashboard1")
def dashboard1():
   try:
      Cursor.execute("select * from enroll_info")
      value = Cursor.fetchall()
      return render_template('dashboard1.html',data1=value)
   except mysql.connector.Error as e:
      print("system error",e)
      return"Error fetching data from the database"
if __name__ == '__main__':
    app.run(debug=True)
