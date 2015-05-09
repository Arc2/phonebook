from flask import Flask, url_for, request, session, g, redirect, Response, jsonify, make_response
from contextlib import closing
import sqlite3

# configuration
DATABASE = 'db/contacts.db'
DEBUG = True
SECRET_KEY = 'development key'
EMAIL = 'admin@admin.com'
PASSWORD = 'admin'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


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
    if request.form['email'] is None:
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
    return "Register"


@app.route('/contacts', methods=['POST', 'GET'])
def contacts():
    return "helol"


@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    return contact_id


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
