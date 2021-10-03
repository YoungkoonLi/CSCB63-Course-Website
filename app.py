# Neccessary imports
import sqlite3
from flask import Flask, session, redirect, url_for, escape, request, render_template, g
# Define app object
app = Flask(__name__)
# Define secret key
app.secret_key = 'George'
# Define the following database, which will be connected later
DATABASE = './assignment3.db'
# A list that hold current user's info.
ACCOUNT = {}
# Following function builds the connection with the database defined above


def get_db():
    # If the database has the meaningful contents, we connect to this database
    db = getattr(g, '_database', None)
    if db is None:
        # otherwise, connect to a new database
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Make tuples in SQL database to dictionaries which easier for python to proceed


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

# This function assist python to proceed SQL queries to database to fetch data


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# When the flask app close, we apply the following function to break down the database connection


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        # close the database if we are connected to it
        db.close()

# home route


@app.route('/')
def index():
    # if the user is logged in then show home page, otherwise redirect to login page(processed by login()).
    if 'Username' in session:
        return render_template("index.html", info=ACCOUNT)
    return redirect(url_for('login'))

# functions for creating a new user

@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'Username' in session:
        return render_template("index.html", info=ACCOUNT)
    elif request.method == 'POST':
        # connect to database
        db = get_db()
        # convert tuples in the database to dictionaries
        db.row_factory = make_dicts
        # Initialcize
        # new cursor and post variable from the database connection
        cur = db.cursor()
        # get request info
        new_user = request.form
        users = query_db("SELECT username FROM Login")
        exist = False
        # check if the username is already used
        for row in users:
            if new_user['username'] == row['username']:
                exist = True
                break
        # insert new user to DB if not already used
        if not exist:
            cur.execute('insert into Login (username, password, type, first, last) values(?, ?, ?, ?, ?)', [
                new_user['username'],
                new_user['password'],
                new_user['type'],
                new_user['first'],
                new_user['last']
            ])
            # also create assignment info for the student. By default, assignment marks are set to
            # empyt string.
            if new_user['type'] == 'student':
                cur.execute('insert into Marks (username, first, last, lab, a1, a2, a3, t1, t2, t3, final) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', [
                    new_user['username'],
                    new_user['first'],
                    new_user['last'],
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    ""
                ])
            # confirm the changes/updates for grade information to the database
            db.commit()
            # close the cursor
            cur.close()
            # close the database
            db.close()
            return redirect(url_for('login'))
        else:
            return render_template("create.html", error=True)
    else:
        return render_template('create.html', error = False)


# This is grades

@app.route('/grades', methods=['GET', 'POST'])
def check_grade():
    if 'Username' not in session:
        return redirect(url_for('login'))
    # connect to the database
    db = get_db()
    # convert tuples in the database to dictionaries
    db.row_factory = make_dicts
    username = session['Username']
    marks = []
    # For instructor users, they will be able to view all students' marks, for student users, they will only be able to view their own marks, for the people without any user account, return 'no username'.
    if username != None:
        if ACCOUNT['type'] == 'instructor':
            marks = query_db('SELECT * From Marks', args=(), one=False)
            # close the database
            db.close()
            return render_template('view_grade.html', grades=marks, info=ACCOUNT)
        else:
            # get marks and remarks for student
            marks = query_db(
                'SELECT * FROM Marks WHERE username = ?', [username], one=False)
            studentremarks = query_db('SELECT * FROM Remark WHERE username = ?', [username], one=False)
            # close the database
            db.close()
            # remove unnecessary info from list of 
            if marks != None and len(marks) > 0:
                marks[0].pop('username')
                marks[0].pop('first')
                marks[0].pop('last')
            return render_template('grade.html', grades=marks, studentremark = studentremarks, info=ACCOUNT)
    else:
        db.close()
        print("None username!")
        return redirect(url_for('login'))

    # You can delete this three lines cuz these lines never met
    # close the database
    db.close()
    return render_template('grade.html', grades=marks, info=ACCOUNT)


@app.route('/changegrade', methods=['GET', 'POST'])
# This function change/update students' grade information into database
def change_grade():
    if 'Username' not in session:
        return redirect(url_for('login'))
    if 'Username' in session:
        # connect to the database
        db = get_db()
        # convert tuples in the database to dictionaries
        db.row_factory = make_dicts
        # Initialize new cursor and post variable from the database connection
        cur = db.cursor()
        new_grade = request.form
        #table = query_db('SELECT * FROM Marks', args=(), one=True)
        # compare assingment type one by one, and give an update of the grade information for each assignment to the database
        if new_grade['Assignment'].lower() == 'a1':
            cur.execute("UPDATE Marks SET a1 = ? WHERE username = ?", [
                        new_grade['Grade'], new_grade['Username']])
        elif new_grade['Assignment'].lower() == 'a2':
            cur.execute("UPDATE Marks SET a2 = ? WHERE username = ?", [
                        new_grade['Grade'], new_grade['Username']])
        elif new_grade['Assignment'].lower() == 'a3':
            cur.execute("UPDATE Marks SET a3 = ? WHERE username = ?", [
                        new_grade['Grade'], new_grade['Username']])
        elif new_grade['Assignment'].lower() == 't1':
            cur.execute("UPDATE Marks SET t1 = ? WHERE username = ?", [
                        new_grade['Grade'], new_grade['Username']])
        elif new_grade['Assignment'].lower() == 't2':
            cur.execute("UPDATE Marks SET t2 = ? WHERE username = ?", [
                        new_grade['Grade'], new_grade['Username']])
        elif new_grade['Assignment'].lower() == 't3':
            cur.execute("UPDATE Marks SET t3 = ? WHERE username = ?", [
                        new_grade['Grade'], new_grade['Username']])
        elif new_grade['Assignment'].lower() == 'final':
            cur.execute("UPDATE Marks SET final = ? WHERE username = ?", [
                        new_grade['Grade'], new_grade['Username']])
        elif new_grade['Assignment'].lower() == 'lab':
            cur.execute("UPDATE Marks SET lab = ? WHERE username = ?", [
                        new_grade['Grade'], new_grade['Username']])
        # confirm the changes/updates for grade information to the database
        db.commit()
        # close the cursor
        cur.close()
        # close the database
        db.close()
        return redirect(url_for('check_grade'))
    return redirect(url_for('login'))

# This is remarkrequest

@app.route('/studentremarkrequest')
# This function display all CSC B63 students' remark request
def getremarkrequest():
    if 'Username' not in session:
        return redirect(url_for('login'))
    # connect to the database
    db = get_db()
    # convert tuples in the database to dictionaries
    db.row_factory = make_dicts
    remarks = []
    for remark in query_db('SELECT * FROM Remark', args=(), one=False):
        remarks.append(remark)
    if ACCOUNT['type'] == 'instructor':
        db.close()
        return render_template('view_remark.html', studentremark=remarks, info=ACCOUNT)
    else:
        db.close()
        return render_template('grade.html', studentremark=[remarks], info=ACCOUNT)
    # close the database

    # maybe can delete this
    db.close()
    return render_template('grade.html', studentremark=[remarks], info=ACCOUNT)





@app.route('/remarkrequest', methods=['POST'])
# This function insert new remark requests for some users(students)
def remarkrequest():
    if 'Username' not in session:
        return redirect(url_for('login'))
    # connect to the database
    db = get_db()
    # convert tuples in the database to dictionaries
    db.row_factory = make_dicts
    # Initialize new cursor and post variable from the database connection
    cur = db.cursor()
    new_remark = request.form
    remarks = query_db('SELECT * FROM Remark', args=(), one=False)
    # After initialize the new cursor and post variable, add remark requests information into the database
    cur.execute('insert into Remark (rid, username, type, reason, status) values(?, ?, ?, ?, ?)', [
        len(remarks)+1,
        session['Username'],
        new_remark['type'],
        new_remark['reason'],
        'pending' # Status of a remark is set to 'pending' by default
    ])
    # confirm the changes/updates for remark requests information to the database
    db.commit()
    # close the cursor
    cur.close()
    # close the database
    db.close()
    return redirect(url_for('check_grade'))

# This is for instructors to handle each remark request
@app.route('/handleremark', methods=['GET', 'POST'])
def handle_remark():
    if 'Username' not in session:
        return redirect(url_for('login'))
    # connect to the database
    db = get_db()
    # convert tuples in the database to dictionaries
    db.row_factory = make_dicts
    # Initialize new cursor and post variable from the database connection
    cur = db.cursor()
    new_remark = request.form
    # After initialize the new cursor and post variable, add/change remark requests information into the database
    cur.execute("UPDATE Remark SET status = ? WHERE rid = ?", [
                        new_remark['status'], new_remark['rid']])
    # confirm the changes/updates for remark requests information to the database
    db.commit()
    # close the cursor
    cur.close()
    # close the database
    db.close()
    return redirect(url_for('getremarkrequest'))
    

# This is for feedbacks

@app.route('/feedback')
# This function display all CSC B63 students' feedbacks
def checkFeedbacks():
    if 'Username' not in session:
        return redirect(url_for('login'))
    # connect to the database
    db = get_db()
    # convert tuples in the database to dictionaries
    db.row_factory = make_dicts
    feedbacks = query_db(
        'SELECT * From Feedback WHERE username = ?', [session['Username']], one=True)
    instructor = query_db('SELECT * FROM Login WHERE type = "instructor"', args=(), one=False)
    # close the database

    # get dict size
    if feedbacks == None:
        length = 0
    else:
        length = len(feedbacks)
    if ACCOUNT['type'] == 'instructor':
        db.close()
        return render_template('view_feedback.html', student_feedback=[feedbacks], info=ACCOUNT, len = length)
    else:
        db.close()
        return render_template('feedback.html', instructors = instructor, info=ACCOUNT)


@app.route('/addfeedback', methods=['POST'])
# This function insert new feedbacks from certain users(students)
def addFeedback():
    if 'Username' not in session:
        return redirect(url_for('login'))
    # connect to the database
    db = get_db()
    # convert tuples in the database to dictionaries
    db.row_factory = make_dicts
    # Initialize new cursor and post variable from the database connection
    cur = db.cursor()
    new_feedback = request.form

    # get dict and it's length
    feedbacks = query_db('SELECT * FROM Feedback', args=(), one=False)
    if feedbacks == None:
        length = 1
    else:
        length = len(feedbacks) + 1
    # After initialize the new cursor and post variable, add feedbacks information into the database
    cur.execute('insert into Feedback (fid, username, q1, q2, q3, q4) values(?, ?, ?, ?, ?, ?)', [
        length,
        new_feedback['username'],
        new_feedback['q1'],
        new_feedback['q2'],
        new_feedback['q3'],
        new_feedback['q4']
    ])
    # confirm the changes/updates for feedbacks information to the database
    db.commit()
    # close the cursor
    cur.close()
    # close the database
    db.close()
    
    return redirect(url_for('checkFeedbacks'))


# route for login

# support both GET and POST request
@app.route('/login', methods=['GET', 'POST'])
def login():
    # if the use is logged in, redirect to home page, otherwise, if this is a POST request,
    # proceed to login, otherwise show the login page.
    if request.method == 'POST':
        # Extract info from request
        username = request.form['Username']
        password = request.form['Password']
        # Validate the username and password. If one of them is not correct, ask the user
        # to re-enter.
        if validate(username, password):
            print("Autheticated.")
            session['Username'] = request.form['Username']
            return redirect(url_for('index'))
        return render_template("login.html", error=True)
    elif 'Username' in session:
        return redirect(url_for('index'))
    else:
        return render_template("login.html", error=False)


#--------------Previous webpages of this website--------------#
@app.route('/lectures')
def lectures():
    # if the user is logged in then show the page, otherwise redirect to login page(processed by login()).
    if 'Username' in session:
        return render_template("lectures.html", info=ACCOUNT)
    return redirect(url_for('login'))

@app.route('/assignments')
def assignments():
    # if the user is logged in then show the page, otherwise redirect to login page(processed by login()).
    if 'Username' in session:
        return render_template("assignment.html", info=ACCOUNT)
    return redirect(url_for('login'))

@app.route('/tutorials')
def tutorial():
    # if the user is logged in then show the page, otherwise redirect to login page(processed by login()).
    if 'Username' in session:
        return render_template("tutorials.html", info=ACCOUNT)
    return redirect(url_for('login'))

@app.route('/staff')
def staff():
    # if the user is logged in then show the page, otherwise redirect to login page(processed by login()).
    if 'Username' in session:
        return render_template("staff.html", info=ACCOUNT)
    return redirect(url_for('login'))

@app.route('/links')
def links():
    # if the user is logged in then show the page, otherwise redirect to login page(processed by login()).
    if 'Username' in session:
        return render_template("links.html", info=ACCOUNT)
    return redirect(url_for('login'))

@app.route('/calendar')
def calendar():
    # if the user is logged in then show the page, otherwise redirect to login page(processed by login()).
    if 'Username' in session:
        return render_template("calendar.html", info=ACCOUNT)
    return redirect(url_for('login'))
#--------------End previous webpages of this website--------------#

#---------------helper functions---------------#
# Search database for the given username and password, returns true iff a match for both username
# and password is found, false otherwise.


def validate(username: str, password: str):
    # write the query
    sql = 'SELECT * FROM Login'
    # query result
    results = query_db(sql, args=(), one=False)
    # loop through the result and compare username&password
    for result in results:
        if result[0] == username:
            if result[1] == password:
                # get user info
                ACCOUNT['username'] = result[0]
                ACCOUNT['type'] = result[2]
                ACCOUNT['first'] = result[3]
                ACCOUNT['last'] = result[4]
                return True
    return False

#---------------End helper functions---------------#
# route for logout


@app.route('/logout')
def logout():
    # clear current user info
    ACCOUNT.clear()
    session.pop('Username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
