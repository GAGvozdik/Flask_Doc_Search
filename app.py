import sqlite3
import os
import csv
from flask import Flask, render_template, request, g

DATABASE = 'test_db.db'
DEBUG = False

app = Flask(__name__)
app.config.from_object(__name__)

# переопределение пути к бд
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'test_db.db')))

# для подключения к бд
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Функция, которая создает базу данных из csv файла posts.csv.
def create_db():
    db = connect_db()
    with app.open_resource('test_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    with open('posts.csv', 'r', encoding="utf8") as f:
        dr = csv.DictReader(f, delimiter=",")
        to_db = [(i['rubrics'], i['text'], i['created_date']) for i in dr]
    cur = db.cursor()
    cur.executemany("INSERT INTO test_db (rubrics, text, created_date) VALUES (?, ?, ?);", to_db)
    db.commit()
    db.close()

# вызывает активное соединение с бд
def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

# авто закрытие соединения
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

# Запрос начальной страницы
@app.route("/")
def index():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM test_db')
    return render_template('index.html', bd = cur.fetchall())

# функция выбирающая и отображающая документы по текстовому запросу, с сортировкой по дате
@app.route('/reg_run', methods=['POST', 'GET'])
def reg_run():
    a = request.form['search']
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM (SELECT * FROM test_db WHERE text LIKE (?) LIMIT 6)", (('%' + a + '%'),))
    result = cur.fetchall()
    print(result)
    return render_template('index.html', bd = result)

# функция для удаления по полю id
def id_del(a):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM test_db WHERE id = ?", (a,))
    db.commit()

# запрос для удаления по полю id
@app.route('/id_delete', methods=['POST', 'GET'])
def id_delete():
    a = request.form['del_choice']
    db = get_db()
    cur = db.cursor()
    id_del(a)
    cur.execute("SELECT * FROM test_db")
    result = cur.fetchall()
    return render_template('index.html', bd = result)

if __name__ == "__main__":
    app.run(debug=True)
