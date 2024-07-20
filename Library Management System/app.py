from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
ITEMS_PER_PAGE = 4
# Database connection setup
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Gayathri@12345',
        database='Library'
    )
    cursor = conn.cursor(dictionary=True)  # Use dictionary cursor for easier data retrieval
except mysql.connector.Error as e:
    print("Error connecting to MySQL database:", e)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']



@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''  # Initialize msg variable here
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM Admins WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['Admin_id'] = account['Admin_id']
            session['username'] = account['username']
            msg = 'Logged in successfully!'
            return redirect(url_for('admin_dashboard'))
        else:
            msg = 'Incorrect username / password!'
    return render_template('login.html', msg=msg)
@app.route('/adminlogout')
def adminlogout():
    session.pop('loggedin', None)
    session.pop('Admin_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if not (username and password and email):
            msg = 'Please fill out the form completely!'
        else:
            cursor.execute('SELECT * FROM Admins WHERE username = %s', (username,))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists!'
            else:
                cursor.execute('INSERT INTO Admins (username, password, email) VALUES (%s, %s, %s)',
                               (username, password, email,))
                conn.commit()
                msg = 'You have successfully registered!'
    return render_template('register.html', msg=msg)
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'loggedin' in session:
        Admin_id = session['Admin_id']
        cursor.execute("SELECT COUNT(*) AS count FROM members")
        members_count = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) AS count FROM books")
        books_count = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) AS count FROM borrowingbooks WHERE status='Borrowed' ")
        borrowed_count = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) AS count FROM borrowingbooks WHERE status='Returned' ")
        returned_count = cursor.fetchone()['count']
        return render_template('admin_dashboard.html', Admin_id=Admin_id,  members_count=  members_count,books_count=books_count,borrowed_count=borrowed_count,returned_count=returned_count)
    else:
        return redirect(url_for('login'))

@app.route('/manage_books', methods=['GET', 'POST'])
def manage_books():
    if 'loggedin' in session:
      
        page = request.args.get('page', 1, type=int)  # Ensure page is an integer
        offset = (page - 1) * ITEMS_PER_PAGE
        
        # Count total items
        cursor.execute('SELECT COUNT(*) AS count FROM books ')
        total_items = cursor.fetchone()['count']  # Use dictionary access to get 'count'
        total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        
        cursor.execute("SELECT * FROM books LIMIT %s OFFSET %s", ( ITEMS_PER_PAGE, offset))
        books = cursor.fetchall()
        
        return render_template('manage_books.html', books=books, page=page, total_pages=total_pages)
    else:
        return redirect(url_for('login'))
@app.route('/add_book/<int:book_id>', methods=['GET', 'POST'])
def add_book(book_id):
    if 'loggedin' in session:
        if request.method == 'POST':
            title = request.form['title']
            author = request.form['author']
            category= request.form['category']
            copies=request.form['copies']
            rack=request.form['rack']
            availability = 'availability' in request.form  # checkbox handling
            file = request.files.get('file')  # Use request.files.get() to safely retrieve file

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                uploads_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
                os.makedirs(uploads_dir, exist_ok=True)
                file_path = os.path.join(uploads_dir, filename)
                file.save(file_path)
            else:
                flash("File type not allowed or no file selected.", 'error')
                return redirect(request.url)  # Redirect back to the form

            # Insert new book into the database
            cursor.execute('INSERT INTO books (title, file, author, category,copies,rack ,availability) VALUES (%s, %s, %s, %s, %s,%s,%s)',
                           (title, filename, author, category,copies,rack ,availability,))
            conn.commit()
            flash("Book added successfully.", 'success')
            return redirect(url_for('manage_books'))

        return render_template('add_book.html', book=None)
    else:
        return redirect(url_for('login'))
@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if 'loggedin' in session:
        if request.method == 'POST':
            title = request.form['title']
            author = request.form['author']
            category = request.form['category']
            copies = request.form['copies']
            rack = request.form['rack']
            availability = 'availability' in request.form  # checkbox handling
            file = request.files.get('file')  # Use request.files.get() to safely retrieve file

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                uploads_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
                os.makedirs(uploads_dir, exist_ok=True)
                file_path = os.path.join(uploads_dir, filename)
                file.save(file_path)

                # Get the filename without the path
                saved_filename = os.path.basename(file_path)
            else:
                flash("File type not allowed or no file selected.", 'error')
                return redirect(request.url)  # Redirect back to the form

            # Update book information in the database
            cursor.execute('UPDATE books SET title=%s, author=%s, category=%s, copies=%s, rack=%s, availability=%s, file=%s WHERE book_id=%s',
                           (title, author, category, copies, rack, availability, saved_filename, book_id))
            conn.commit()
            flash("Book updated successfully.", 'success')
            return redirect(url_for('manage_books', book_id=book_id))

        # Fetch book information for editing
        cursor.execute('SELECT * FROM books WHERE book_id = %s', (book_id,))
        book = cursor.fetchone()
        return render_template('edit_book.html', book=book, book_id=book_id)
    else:
        return redirect(url_for('login'))
@app.route('/delete_book/<int:book_id>', methods=['GET', 'POST'])
def delete_book(book_id):
    if 'loggedin' in session:
        
          
            cursor.execute('DELETE FROM books WHERE book_id = %s', (book_id,))
            conn.commit()
            return redirect(url_for('manage_books'))
     
    else:
        return redirect(url_for('login'))

@app.route('/view_book/<int:book_id>', methods=['POST', 'GET'])
def view_book(book_id):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
        book = cursor.fetchone()
    except mysql.connector.Error as e:
        print("Error executing SQL query:", e)
        book = None
    return render_template('view_book.html', book=book, book_id=book_id)
@app.route('/manage_members', methods=['GET', 'POST'])
def manage_members():
    if 'loggedin' in session:
        # Initialize variables
        members = []
        total_pages = 0
        
        if request.method == 'POST':
            search_keyword = request.form.get('search_keyword', '')
            page = request.args.get('page', 1, type=int)  # Ensure page is an integer
            offset = (page - 1) * ITEMS_PER_PAGE
            
            # Count total items matching search criteria
            cursor.execute('SELECT COUNT(*) AS count FROM members WHERE name LIKE %s OR email LIKE %s',
                           ('%' + search_keyword + '%', '%' + search_keyword + '%'))
            total_items = cursor.fetchone()['count']  # Use dictionary access to get 'count'
            total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            
            # Fetch members based on search criteria with pagination
            cursor.execute("SELECT * FROM members WHERE name LIKE %s OR email LIKE %s LIMIT %s OFFSET %s",
                           ('%' + search_keyword + '%', '%' + search_keyword + '%', ITEMS_PER_PAGE, offset))
            members = cursor.fetchall()
        else:
            # Fetch all members without any search filter with pagination
            page = request.args.get('page', 1, type=int)  # Ensure page is an integer
            offset = (page - 1) * ITEMS_PER_PAGE
            
            cursor.execute('SELECT COUNT(*) AS count FROM members')
            total_items = cursor.fetchone()['count']  # Total count of members
            
            total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            
            cursor.execute("SELECT * FROM members LIMIT %s OFFSET %s", (ITEMS_PER_PAGE, offset))
            members = cursor.fetchall()
        
        return render_template('manage_members.html', members=members,page=page, total_pages=total_pages)
    else:
        return redirect(url_for('login'))

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']

            if not (name and email and password):
                msg = 'Please fill out the form completely!'
            else:
                cursor.execute('INSERT INTO members (name, email, password) VALUES (%s, %s, %s)',
                               (name, email, password,))
                conn.commit()
                flash("Member added successfully.", 'success')
                return redirect(url_for('manage_members'))

        return render_template('add_member.html', msg=msg)  # Ensure msg is passed here
    else:
        return redirect(url_for('login'))
@app.route('/edit_member/<int:member_id>', methods=['GET', 'POST'])
def edit_member(member_id):
    msg = ''
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM members WHERE member_id = %s', (member_id,))
        member = cursor.fetchone()

        if member is None:
            flash("Member not found.", 'error')
            return redirect(url_for('manage_members'))

        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']

            if not (name and email):
                msg = 'Please fill out the form completely!'
            else:
                if password:
                    cursor.execute('UPDATE members SET name=%s, email=%s, password=%s WHERE member_id=%s',
                                   (name, email, password, member_id))
                else:
                    cursor.execute('UPDATE members SET name=%s, email=%s WHERE member_id=%s',
                                   (name, email, member_id))
                conn.commit()
                flash("Member updated successfully.", 'success')
                return redirect(url_for('manage_members'))

        return render_template('edit_member.html', member=member, member_id=member_id, msg=msg)  # Pass member_id here
    else:
        return redirect(url_for('login'))
@app.route('/delete_member/<int:member_id>', methods=['POST', 'GET'])
def delete_member(member_id):
    if 'loggedin' in session:
        cursor.execute('DELETE FROM members WHERE member_id = %s', (member_id,))
        conn.commit()
        flash("Member deleted successfully.", 'success')
        return redirect(url_for('manage_members'))
    else:
        return redirect(url_for('login'))
@app.route('/view_member/<int:member_id>', methods=['GET', 'POST'])
def view_member(member_id):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
        member = cursor.fetchone()
    except mysql.connector.Error as e:
        print("Error executing SQL query:", e)
        member = None  # Set member to None in case of an error

    if member is None:
        flash("Member not found.", 'error')
        return redirect(url_for('manage_members'))

    return render_template('view_member.html', member=member)
@app.route('/borrowed_books', methods=['GET', 'POST'])
def borrowed_books():
    if 'loggedin' in session:
        page = request.args.get('page', 1, type=int)  # Ensure page is an integer
        offset = (page - 1) * ITEMS_PER_PAGE
        
        # Count total items
        cursor.execute('SELECT COUNT(*) AS count  FROM borrowingbooks where status="borrowed"  ')
        total_items = cursor.fetchone()['count']  # Use dictionary access to get 'count'
        total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        
        cursor.execute("SELECT * FROM borrowingbooks LIMIT %s OFFSET %s", ( ITEMS_PER_PAGE, offset))
        books = cursor.fetchall()
      
        return render_template('borrowed_books.html', books=books,page=page,total_pages=total_pages)
    else:
        return redirect(url_for('login'))
@app.route('/returned_books', methods=['GET', 'POST'])
def returned_books():
    if 'loggedin' in session:
        page = request.args.get('page', 1, type=int)  # Ensure page is an integer
        offset = (page - 1) * ITEMS_PER_PAGE
        
        # Count total items
        cursor.execute('SELECT COUNT(*) AS count from  borrowingbooks where status="Returned" ')
        total_items = cursor.fetchone()['count']  # Use dictionary access to get 'count'
        total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        
        cursor.execute("SELECT * FROM borrowingbooks LIMIT %s OFFSET %s", ( ITEMS_PER_PAGE, offset))
        books = cursor.fetchall()
       
        return render_template('returned_books.html', books=books,page=page,total_pages=total_pages)
    else:
        return redirect(url_for('login'))
@app.route('/books', methods=['GET', 'POST'])
def book():
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM books')
        book = cursor.fetchall()
        return render_template('books.html', book=book)
    else:
        return redirect(url_for('login'))
@app.route('/')
def index():
  
    return render_template('index.html')

@app.route('/user/memberlogin', methods=['GET', 'POST'])
def memberlogin():
    msg = ''
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        cursor.execute('SELECT * FROM members WHERE name = %s', (name,))
        account = cursor.fetchone()
        
        if account and account['password'] == password:  
            session['loggedin'] = True
            session['member_id'] = account['member_id']
            session['username'] = account['name']
            msg = 'Logged in successfully!'
            return redirect(url_for('home'))  # Redirect to home page after successful login
        else:
            msg = 'Incorrect username / password!'
    
    return render_template('memberlogin.html', msg=msg)

@app.route('/logout')
def logout():
    session.clear()  # Clear all session variables
    return redirect(url_for('memberlogin'))

@app.route('/user/memberregister', methods=['GET', 'POST'])
def memberregister():
    msg = ''
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']

        if not (name and password and email):
            msg = 'Please fill out the form completely!'
        else:
            cursor.execute('SELECT * FROM members WHERE name = %s', (name,))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists!'
            else:
                cursor.execute('INSERT INTO members (name, password, email) VALUES (%s, %s, %s)',
                               (name, password, email,))
                conn.commit()
                msg = 'You have successfully registered!'
    
    return render_template('memberregister.html', msg=msg)

@app.route('/user/borrow_book', methods=['GET', 'POST'])
def borrow_book():
    if 'loggedin' in session:
        print("request method:",request.method)
        if request.method == 'POST':
            try:
                book_id = request.form['book_id']
                title = request.form['title']
                member_id = session['member_id']
                borrow_date = datetime.now().strftime('%Y-%m-%d')
                due_date = request.form['due_date']
                
                # Insert new borrowing record into the database
                cursor.execute('INSERT INTO borrowingbooks (book_id, member_id, title, borrow_date, due_date) VALUES (%s, %s, %s, %s, %s)',
                               (book_id, member_id, title, borrow_date, due_date))
                conn.commit()
                
                # Update the status of the book to "Borrowed"
                cursor.execute('UPDATE borrowingbooks SET status = %s WHERE book_id = %s', ('Borrowed', book_id))
                conn.commit()
                
                # Redirect to the borrowing history page
                return redirect(url_for('history', member_id=member_id))
            
            except mysql.connector.Error as err:
                # Handle database errors (e.g., print error details, rollback transaction)
                print(f"Database error: {err}")
                conn.rollback()
               
            except ValueError as e:
               
                print(f"Invalid data: {e}")
             
        else:
            print("I am inside get")
           
            book_id = request.args.get('book_id')
            title=request.args.get('title')
            return render_template('borrow_book.html', book_id=book_id,title=title)
          
    # Redirect to login page if not logged in or for any other errors
    return redirect(url_for('memberlogin'))


@app.route('/return_book', methods=['POST', 'GET'])
def return_book():
    if 'loggedin' in session:
        if request.method == 'POST':
            book_id = request.form['book_id']
            member_id = session['member_id']
            return_date = datetime.now().strftime('%Y-%m-%d')
            
            try:
                # Update the return date in the borrowingbooks table
                cursor.execute('UPDATE borrowingbooks SET return_date = %s WHERE book_id = %s AND member_id = %s',
                               (return_date, book_id, member_id))
                conn.commit()
                
                # Update the status of the book to "Returned" in the books table
                cursor.execute('UPDATE borrowingbooks SET return_date = %s, status = %s WHERE book_id = %s AND member_id = %s',
                (return_date, 'Returned', book_id, member_id))

                
                # Redirect to the borrowing history page
                return redirect(url_for('history', member_id=member_id))
            
            except mysql.connector.Error as e:
                flash(f"Error returning book: {e}", 'error')
                return redirect(url_for('history', member_id=member_id))  # Redirect even if error occurs
        
        return render_template('returnbook.html')  # Render the template for GET request
    else:
        return redirect(url_for('memberlogin'))  # Redirect if not logged in
  # Redirect if not logged in
@app.route('/home')
def home():
    # Assuming you fetch member details from the database
    member = {'member_id': session.get('member_id', None), 'name': session.get('username', None), 'email': 'example@email.com'}
    return render_template('home.html', member=member)
@app.route('/user_book', methods=['GET', 'POST'])
def user_book():
        
        cursor.execute('SELECT * FROM books')
        books = cursor.fetchall()
        return render_template('user_book.html',books=books)

@app.route('/borrow_history/<int:member_id>', methods=['POST','GET'])
def history(member_id):
    if 'loggedin' in session:
        if request.method == 'GET':
            try:
                page = request.args.get('page', 1, type=int)  # Ensure page is an integer
                offset = (page - 1) * ITEMS_PER_PAGE
                cursor.execute('SELECT COUNT(*) AS count FROM borrowingbooks WHERE member_id = %s', (member_id,))
                total_items = cursor.fetchone()['count']  # Use dictionary access to get 'count'
                total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        
                cursor.execute("SELECT * FROM borrowingbooks LIMIT %s OFFSET %s", ( ITEMS_PER_PAGE, offset))
                books = cursor.fetchall()
                
                return render_template('borrow_history.html', books=books, member_id=member_id,page=page, total_pages=total_pages)
            except mysql.connector.Error as e:
                return f"Error fetching borrowing history: {e}"
    else:
        return redirect(url_for('memberlogin'))


if __name__ == '__main__':
    app.run(debug=True)
