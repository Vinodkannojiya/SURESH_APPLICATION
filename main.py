import pymysql
import sys
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hjshjhdjahkjshkjdhjs'

class Database():
    def __init__(self):
        host = "localhost"
        user = "root"
        password = "mysql-root-password"
        db = "learning"
        self.con = pymysql.Connect(host=host, user=user, password=password, db=db,
                                   cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.con.cursor()

    def create_user(self,username,password):
        self.cur.execute(f"insert into user_table (username, password) "
                         f"values (%s,%s)",
                         (username, password))
        self.con.commit()

    def check_user(self,username):
        self.cur.execute(f"select username,password from user_table where username ='{username}'")
        res = self.cur.fetchall()
        return res

    

    def submit_responses(self, username, sub_name, res1, res2, res3, res4, res5, res6, res7, res8, res9, res10):
        responses = [res1, res2, res3, res4, res5, res6, res7, res8, res9, res10]
        self.cur.execute("INSERT INTO response_table(user_name,subject_name,date_of_exam,res1,res2,res3,res4,res5,res6,res7,res8,res9,res10)"
                         " VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (username, sub_name, datetime.now(), res1, res2, res3, res4, res5, res6, res7, res8, res9, res10))
        self.con.commit()

        self.cur.execute(f"select  ans1, ans2,ans3,ans4,ans5,ans6,ans7,ans8,ans9,ans10 from answer_table where subject_name='{sub_name}'")
        output = self.cur.fetchall()[0]
        answers = [output['ans1'],output['ans2'],output['ans3'],output['ans4'],output['ans5'],output['ans6'],output['ans7'],output['ans8'],output['ans9'],output['ans10']]
        sum_of_correct_ans = 0

        for i in range(10):
            if answers[i] == responses[i]:
                sum_of_correct_ans += 1
        total_questions = 10
        percentage = (sum_of_correct_ans/total_questions) * 100
        self.cur.execute(f"insert into result_table (user_name,subject_name,date_of_exam,score,total,percentage) "
                         f"values (%s,%s,%s,%s,%s,%s)",
                         (username,sub_name,datetime.now(),sum_of_correct_ans,total_questions,percentage))
        self.con.commit()

    def get_all_users(self):
        self.cur.execute(f"select * from user_table")
        res = self.cur.fetchall()
        return res




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Database().check_user(username)
        if user:
            user = user[0]
            if user['password'] == password:
                session['logged_in'] = True
                session['username'] = username
                flash('Logged in successfully!', category='success')
                if  user['username'] == 'admin':
                    return redirect("/admin")
                else:
                    return redirect("/")
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('User does not exist.', category='error')

    return render_template("login.html")


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Database().check_user(username)
        if user:
            flash('User already exists.', category='error')
        elif len(username) < 4:
            flash('Username must be greater than 3 characters.', category='error')
        elif len(password) < 5:
            flash('Password must be at least 5 characters.', category='error')
        else:
            Database().create_user(username, password)
            flash('Account created!', category='success')
            return redirect("/login")

    return render_template("sign_up.html")


def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, please login','danger')
            return redirect('/login')
    return wrap


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('you are now logged out ','success')
    return redirect('/login')


@app.route("/", methods=['GET','POST'])
@is_logged_in
def home():
    if request.method == 'POST':
        pass
    else:
        username = session['username']
        status = Database().get_user_result_status(username)
        return render_template("home.html",status=status)


@app.route("/member", methods=['GET','POST'])
@is_logged_in
def member():
    # sub = Database().list_of_subjects()
    return render_template("member.html")



@app.route("/question", methods=['POST'])
@is_logged_in
def question_response():
    username = session['username']
    sub_name = request.form.get('sub_name')
    res1 = request.form.get('1')
    res2 = request.form.get('2')
    res3 = request.form.get('3')
    res4 = request.form.get('4')
    res5 = request.form.get('5')
    res6 = request.form.get('6')
    res7 = request.form.get('7')
    res8 = request.form.get('8')
    res9 = request.form.get('9')
    res10 = request.form.get('10')
    Database().submit_responses(username, sub_name, res1, res2, res3, res4, res5, res6, res7, res8, res9, res10)
    return redirect("/result")








@app.route("/all_users", methods=['GET','POST'])
@is_logged_in
def all_users():
    res = Database().get_all_users()
    return render_template("admin.html", user=res)




@app.route("/admin", methods=['GET','POST'])
def admin_page():
    if request.method == 'POST':
        res = Database().get_content_data()
        return render_template("admin.html", content=res)
    else:
        username = session['username']
        if username == 'admin':
            res = Database().get_content_data()
            return render_template("admin.html", content=res)
        return render_template("login.html")


if __name__ == "__main__":
    app.run(port=5005,debug=True)