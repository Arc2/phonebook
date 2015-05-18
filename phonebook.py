from flask import Flask, url_for, request, session, g, redirect, Response, jsonify, make_response, abort
from contextlib import closing
import sqlite3

# configuration
DATABASE = 'db/phonebook.db'
DEBUG = True
SECRET_KEY = 'development key'
EMAIL = 'admin@admin.com'
PASSWORD = 'admin'

app = Flask(__name__)
app.config.from_object(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_db()
    return db


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def hello_world():
    return "Hello World!"


@app.route('/login', methods=['POST'])
def login():
    cur = g.db.execute('SELECT email, password, uid FROM accounts ORDER BY uid ASC')
    # credentials = [dict(email=row[0], password=row[1]) for row in cur.fetchall()]
    # if request.json['email'] in credentials:
    return jsonify(status="ok", uid=2)


@app.route('/account', methods=['GET'])
def account_info():
    res = jsonify(uid=2, email="email@gmail.com")
    return res


@app.route('/logout', methods=['POST'])
def logout():
    return jsonify(status="ok")


@app.route('/register', methods=['POST'])
def register():
    mail = request.json['email']
    g.db.execute('INSERT INTO accounts (email, password) VALUES (?, ?)',
                 [mail, request.json['password']])
    g.db.commit()
    user = query_db('SELECT email, uid FROM accounts WHERE email = ?',
                    [mail], one=True)
    return user['uid']
    # return jsonify(status="ok", uid="2")


@app.route('/contacts', methods=['POST', 'GET'])
def contacts():
    if request.method == 'POST':
        contact = request.json
        contact['uid'] = 2
        contact['id'] = 1
        g.db.execute('INSERT INTO contacts (id, name, telephone, address, comment, owner) VALUES (NULL, ?, ?, ?, ?, ?)',
                     [contact['name'], contact['telephone'], contact['address'],
                      contact['comment'], contact['uid']])
        g.db.commit()
        return jsonify(contact)
    if request.method == 'GET':
        uid = 2
        cur = g.db.execute(
            'SELECT id, name, telephone, address, comment, owner FROM contacts WHERE owner = ?',
            [uid])
        contacts_dict = [dict(id=row[0], name=row[1], telephone=row[2], address=row[3], comment=row[4], owner=row[5])
                         for row in
                         cur.fetchall()]
        return jsonify({'contacts': contacts_dict})


@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    uid = 2
    g.db.execute('DELETE FROM contacts WHERE id = ? AND owner = ?',
                 [contact_id, uid])
    g.db.commit()
    return Response(status=204)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
