import random

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
    shuffle(result)
    return result

def clear_coockies():
    session['check_task'] = 0
    session['word_num'] = 0
    session['score'] = 0
    session['status'] = [0] * 10
    session['answer'] = [('', '')] * 10
@app.route('/')

@app.route('/login', methods=['GET'])
def login():
    if request.method == 'GET':
        username = request.args.get('username')
        password = request.args.get('password')

        conn = connect('Individual_project.db')
        cursor = conn.cursor()
        result = cursor.execute("""SELECT * FROM Users WHERE Username = ? AND Password = ?""", (username, password)).fetchone()
        check_username = bool(cursor.execute("""SELECT * FROM Users WHERE Username = ?""", (username,)).fetchone())
        conn.commit()
        conn.close()

        if result and username:
            session['username'] = username
            session['check_task'] = 0
            return redirect(url_for('home'))
        elif check_username:
            return render_template('login.html', message='Неверный пароль')
        elif username:
            return render_template('login.html', message='Неверный логин')
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

        if len(result) == 0 and username:
            if password == password_again and username:
                cursor.execute("""INSERT INTO Users(Username, Password, all_task1, accept_task1) VALUES(?, ?, ?, ?)""",
                               (username, password, 0, 0))
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
        l = set()
        while len(l) != 10:
            l.add(cursor.execute("""SELECT word FROM words_task_1 WHERE ID = ?""", (randint(0, 222),)).fetchone()[0].replace('Ё', 'Е'))
        conn.close()
        l = list(l)
        session['check_task'] = 1
        session['word_num'] = 0
        session['score'] = 0
        session['list'] = l
        session['list_ans'] = list_ans(l[0])
        return render_template('task1.html')
    elif request.method == 'GET' and request.args.get('answer'):
        answer = request.args.get('answer')
        word = session['list'][session['word_num']]
        if answer == word:
            session['score'] += 1
        else:
            session['status'][session['word_num']] = 1
        session['answer'][session['word_num']] = (answer, word)
        session['word_num'] += 1
        if session['word_num'] < 10:
            session['list_ans'] = list_ans(session['list'][session['word_num']])
            return render_template('task1.html')
        else:
            return redirect(url_for('result'))
    return render_template('task1.html')


@app.route('/result')
def result():
    username = session['username']
    conn = connect('Individual_project.db')
    cursor = conn.cursor()
    result = cursor.execute("""SELECT accept_task1, all_task1 FROM Users WHERE Username = ?""", (username,)).fetchone()
    accept_task1 = result[0]
    all_task1 = result[1]
    accept_task1 = accept_task1 + session['score']
    all_task1 += 10
    result = cursor.execute("""UPDATE Users SET accept_task1 = ?, all_task1 = ? WHERE Username = ?""", (accept_task1, all_task1, username)).fetchone()
    conn.commit()
    conn.close()
    score = session['score']
    status = session['status']
    answer = session['answer']
    clear_coockies()
    return render_template('result.html', score=score, status=status, answer=answer)

@app.route('/home')
def home():
    clear_coockies()
    return render_template('home.html')


@app.route('/logout')
def logout():
    session['username'] = None
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    conn = connect("Individual_project.db")
    username = session['username']
    conn = connect('Individual_project.db')
    cursor = conn.cursor()
    result = cursor.execute("""SELECT accept_task1, all_task1 FROM Users WHERE Username = ?""", (username,)).fetchone()
    accept_task1 = result[0]
    all_task1 = result[1]
    conn.commit()
    conn.close()
    return render_template('profile.html', score=int(accept_task1 * 100 / max(all_task1, 1)))

@app.route('/teoriy')
def teoriy():
    return render_template('teoriy.html')

@app.route('/trophy')
def trophy():
    conn = connect("Individual_project.db")
    cursor = conn.cursor()
    result = cursor.execute("""SELECT accept_task1, all_task1, Username FROM Users """).fetchall()
    a = []
    for (ac, al, us) in result:
        a.append((-int(ac * 100/ max(1, al)), us))
    a.sort()
    return render_template('trophy.html', rat=a, size=len(a))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)