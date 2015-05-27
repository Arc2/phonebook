from flask import Flask, request, session, g, Response, jsonify, abort
from contextlib import closing
import sqlite3

# configuration
DATABASE = 'db/phonebook.db'
SECRET_KEY = 'development key'

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


def is_valid_login(credentials):
    # error = None
    cur = g.db.execute('SELECT email, password FROM accounts WHERE email = ?',
                       [credentials["email"]])
    for row in cur:
        if dict(email=row[0], password=row[1]) == credentials:
            return True
    return False


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/login', methods=['POST'])
def login():
    if 'uid' in session:
        abort(400)
    credentials = dict(email=request.json['email'], password=request.json['password'])
    cur = g.db.execute(
        'SELECT uid FROM accounts WHERE email = ?',
        [credentials["email"]])

    if is_valid_login(credentials):
        session['email'] = credentials["email"]
        for row in cur:
            session['uid'] = row[0]
        return jsonify(status="ok", uid=session['uid'])
    else:
        abort(404)


@app.route('/account', methods=['GET'])
def account_info():
    if 'uid' not in session:
        abort(401)
    res = jsonify(uid=session['uid'], email=session['email'])
    return res


@app.route('/logout', methods=['POST'])
def logout():
    if 'uid' not in session:
        abort(401)
    session.pop('email', None)
    session.pop('uid', None)
    return jsonify(status="ok")


@app.route('/register', methods=['POST'])
def register():
    cur = g.db.execute(
        'SELECT uid FROM accounts WHERE email = ?',
        [request.json["email"]])
    for row in cur:
        abort(403)
    g.db.execute('INSERT INTO accounts (email, password) VALUES (?, ?)',
                 [request.json['email'], request.json['password']])
    g.db.commit()
    user = query_db('SELECT uid FROM accounts WHERE email = ?',
                    [request.json['email']], one=True)
    session['email'] = request.json['email']
    session['uid'] = user[0]
    return jsonify(status="ok", uid=session['uid'])


@app.route('/contacts', methods=['POST', 'GET'])
def contacts():
    if 'uid' not in session:
        abort(401)
    if request.method == 'POST':
        contact = request.json
        contact['uid'] = session['uid']
        g.db.execute('INSERT INTO contacts (id, name, telephone, address, comment, owner) VALUES (NULL, ?, ?, ?, ?, ?)',
                     [contact['name'], contact['telephone'], contact['address'],
                      contact['comment'], contact['uid']])
        g.db.commit()
        contact['id'] = None
        cur = g.db.execute('SELECT id FROM contacts ORDER BY id DESC')
        for row in cur.fetchall():
            contact['id'] = row[0]
        return jsonify(contact)
    if request.method == 'GET':
        cur = g.db.execute(
            'SELECT id, name, telephone, address, comment, owner FROM contacts WHERE owner = ?',
            [session['uid']])
        contacts_dict = [dict(id=row[0], name=row[1], telephone=row[2], address=row[3], comment=row[4], owner=row[5])
                         for row in
                         cur.fetchall()]
        return jsonify({'contacts': contacts_dict})


@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    if 'uid' not in session:
        abort(401)
    cur = g.db.execute('SELECT id, name, telephone, address, comment, owner FROM contacts WHERE owner = ?',
                       [session['uid']])
    for row in cur.fetchall():
        if row is not None:
            g.db.execute('DELETE FROM contacts WHERE id = ? AND owner = ?',
                         [contact_id, session['uid']])
            g.db.commit()
            return Response(status=204)
    abort(404)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
