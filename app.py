import random

from flask import *
from sqlite3 import *
from random import *
from json import *

app = Flask(__name__)
app.secret_key = 'f8hwt6be'

base_stat = [(0, 0)] * 223


def list_ans(s):
    a = 'ёеуэоаыяию'
    result = []
    t = s.lower()
    for i in range(len(t)):
        if t[i] in a:
            result.append(t[0:i] + t[i].upper() + t[i + 1:])
    shuffle(result)
    return result


def check_username(username):
    s = "1234567890qwertyuioplkjhgfdsazxcvbnm_QWERTYUIOPLKJHGFDSAZXCVBNM"
    for i in username:
        if i not in s:
            return False
    return True and 30 >= len(username) >= 5


def check_password(password):
    s = "012345qwertyuiopasdfghjQWERTYUIOPASDFGHJKLZXCVBNMklzxcvbnm6789"
    for i in password:
        if i not in s:
            return False
    return 30 >= len(password) >= 8


def password_hash(password):
    h = 0
    x = 12345
    mod = 10 ** 9 + 21
    for i in password:
        h = (h * x + ord(i)) % mod
    return h


def clear_coockies():
    session['check_task'] = 0
    session['word_num'] = 0
    session['score'] = 0
    session['status'] = [0] * 10
    session['answer'] = [('', '')] * 10


def words(username):
    conn = connect('data_base.db')
    cursor = conn.cursor()
    result = loads(cursor.execute("""SELECT statistika FROM Users WHERE Username = ?""", (username,)).fetchone()[0])
    for i in range(len(result)):
        a, b = result[i]
        result[i] = (a + randint(-3, 3), b + randint(-3, 3), i)
    result.sort()
    l = []
    for i in range(10):
        l.append((cursor.execute("""SELECT word FROM words_task_1 WHERE ID = ?""", (result[i][2] + 1,)).fetchone()[
                      0].replace('Ё', 'Е'), result[i][2]))
    conn.close()
    return l


@app.route('/')
@app.route('/login', methods=['GET'])
def login():
    if request.method == 'GET':
        username = request.args.get('username')
        password = request.args.get('password')

        conn = connect('data_base.db')
        cursor = conn.cursor()
        if not username or not password:
            return render_template('login.html', message='')
        result = cursor.execute("""SELECT * FROM Users WHERE Username = ? AND Password = ?""",
                                (username, password_hash(password))).fetchone()
        check_username = bool(cursor.execute("""SELECT * FROM Users WHERE Username = ?""", (username,)).fetchone())
        conn.commit()
        conn.close()

        if result and username:
            session['username'] = username
            clear_coockies()
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

        if username and not check_username(username):
            return render_template('register.html',
                                   message='Логин может содержать только символы A-Z, a-z, 0-9, "_" и иметь длину от 7 до 30')

        if password and not check_password(password):
            return render_template('register.html',
                                   message='Пароль должен иметь длину больше 7 символов и содержать символы A-Z, a-z, 0-9 и иметь длину от 7 до 30')

        conn = connect('data_base.db')
        cursor = conn.cursor()
        result = cursor.execute("""SELECT * FROM Users WHERE Username = ?""", (username,)).fetchall()

        if len(result) == 0 and username:
            if password == password_again and username:
                cursor.execute(
                    """INSERT INTO Users(Username, Password, all_task1, accept_task1, statistika) VALUES(?, ?, ?, ?, ?)""",
                    (username, password_hash(password), 0, 0, dumps(base_stat)))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
            return render_template('register.html', message='Не совпадают пароли')
        elif username:
            conn.close()
            return render_template('register.html', message='Имя пользователя занято')
    return render_template('register.html')


@app.route('/task1', methods=['GET'])
def task1():
    if not session['username']:
        return redirect(url_for('login'))
    if not session['check_task']:
        l = words(session['username'])
        session['check_task'] = 1
        session['word_num'] = 0
        session['score'] = 0
        session['list'] = l
        session['list_ans'] = list_ans(l[0][0])
        return render_template('task1.html')
    elif request.method == 'GET' and request.args.get('answer'):
        answer = request.args.get('answer')
        word = session['list'][session['word_num']][0]
        if answer == word:
            session['score'] += 1
        else:
            session['status'][session['word_num']] = 1
        session['answer'][session['word_num']] = (answer, word)
        session['word_num'] += 1
        if session['word_num'] < 10:
            session['list_ans'] = list_ans(session['list'][session['word_num']][0])
            return render_template('task1.html', score=session['score'])
        else:
            return redirect(url_for('result'))
    return render_template('task1.html')


@app.route('/result')
def result():
    if not session['username']:
        return redirect(url_for('login'))
    username = session['username']
    conn = connect('data_base.db')
    cursor = conn.cursor()
    result = cursor.execute("""SELECT accept_task1, all_task1 FROM Users WHERE Username = ?""", (username,)).fetchone()
    accept_task1 = result[0]
    all_task1 = result[1]
    accept_task1 = accept_task1 + session['score']
    all_task1 += 10
    result = cursor.execute("""UPDATE Users SET accept_task1 = ?, all_task1 = ? WHERE Username = ?""",
                            (accept_task1, all_task1, username)).fetchone()
    result = loads(cursor.execute("""SELECT statistika FROM Users WHERE Username = ?""", (username,)).fetchone()[0])
    for i in range(10):
        s, it = session['list'][i]
        a, b = result[it]
        if session['status'][i] == 1:
            result[it] = (a + 1, b - 10)
        else:
            result[it] = (a + 1, b + 7)

    result = cursor.execute("""UPDATE Users SET statistika = ? WHERE Username = ?""",
                            (dumps(result), username)).fetchone()

    conn.commit()
    conn.close()
    score = session['score']
    status = session['status']
    answer = session['answer']
    clear_coockies()
    return render_template('result.html', score=score, status=status, answer=answer)


@app.route('/home')
def home():
    if not session['username']:
        return redirect(url_for('login'))
    clear_coockies()
    return render_template('home.html')


@app.route('/logout')
def logout():
    if not session['username']:
        return redirect(url_for('login'))
    session['username'] = None
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    if not session['username']:
        return redirect(url_for('login'))
    conn = connect("data_base.db")
    username = session['username']
    conn = connect('data_base.db')
    cursor = conn.cursor()
    result = cursor.execute("""SELECT accept_task1, all_task1 FROM Users WHERE Username = ?""", (username,)).fetchone()
    accept_task1 = result[0]
    all_task1 = result[1]
    conn.commit()
    conn.close()
    return render_template('profile.html', score=int(accept_task1 * 100 / max(all_task1, 1)))


@app.route('/teoriy')
def teoriy():
    if not session['username']:
        return redirect(url_for('login'))
    return render_template('teoriy.html')


@app.route('/trophy')
def trophy():
    if not session['username']:
        return redirect(url_for('login'))
    conn = connect("data_base.db")
    cursor = conn.cursor()
    result = cursor.execute("""SELECT accept_task1, all_task1, Username FROM Users """).fetchall()
    a = []
    for (ac, al, us) in result:
        a.append((-int(ac * 100 / max(1, al)), us))
    a.sort()
    return render_template('trophy.html', rat=a, size=len(a))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
