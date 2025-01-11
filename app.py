from flask import *
from sqlite3 import *
from random import *


app = Flask(__name__)
app.secret_key = 'f8hwt6be'

def list_ans(s):
    a = 'ёеуэоаыяию'
    result = []
    t = s.lower()
    for i in range(len(t)):
        if t[i] in a:
            result.append(t[0:i] + t[i].upper() + t[i + 1:])
    return result

def clear_coockies():
    session['check_task'] = 0
    session['word_num'] = 0
    session['score'] = 0
@app.route('/')

@app.route('/login', methods=['GET'])
def login():
    if request.method == 'GET':
        username = request.args.get('username')
        password = request.args.get('password')

        conn = connect('Individual_project.db')
        cursor = conn.cursor()
        result = cursor.execute("""SELECT * FROM Users WHERE Username = ? AND Password = ?""", (username, password)).fetchone()
        conn.commit()
        conn.close()

        if result:
            session['username'] = username
            session['check_task'] = 0
            return redirect(url_for('home'))
        elif username:
            return render_template('login.html', message='Неверный пароль')
    return render_template('login.html', message='')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        username = request.args.get('username')
        password = request.args.get('password')
        password_again = request.args.get('password_again')

        conn = connect('Individual_project.db')
        cursor = conn.cursor()
        result = cursor.execute("""SELECT * FROM Users WHERE Username = ?""", (username,)).fetchall()

        response = make_response(render_template('register.html'))

        if len(result) == 0 and username:
            if password == password_again and username:
                cursor.execute("""INSERT INTO Users(Username, Password, Points) VALUES(?, ?, ?)""",
                               (username, password, 0))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
            return render_template('register.html', message='Несовпадают пароли')
        elif username:
            conn.close()
            return render_template('register.html', message='Имя пользователя занято')
    return render_template('register.html')


@app.route('/task1', methods=['GET'])
def task1():
    if not session['check_task']:
        conn = connect('Individual_project.db')
        cursor = conn.cursor()
        list = []
        for i in range(10):
            list.append(cursor.execute("""SELECT word FROM words_task_1 WHERE ID = ?""", (randint(0, 222),)).fetchone()[0])
        conn.close()

        session['check_task'] = 1
        session['word_num'] = 0
        session['score'] = 0
        session['list'] = list
        session['list_ans'] = list_ans(list[0])
        return render_template('task1.html')
    elif request.method == 'GET' and request.args.get('answer'):
        answer = request.args.get('answer')
        word = session['list'][session['word_num']]
        if answer == word:
            session['score'] += 1
        session['word_num'] += 1
        if session['word_num'] < 10:
            session['list_ans'] = list_ans(session['list'][session['word_num']])
            return render_template('task1.html')
        else:
            clear_coockies()
            return render_template('result.html')
    return render_template('task1.html')


@app.route('/result')
def result():
    clear_coockies()
    return render_template('result.html')

@app.route('/home')
def home():
    clear_coockies()
    return render_template('home.html')

@app.route('/profile')
def profile():
    clear_coockies()
    return render_template('profile.html')

if __name__ == '__main__':
    app.run()