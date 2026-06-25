import os
import psycopg2
from psycopg2.extras import DictCursor
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required
from dotenv import load_dotenv

# .env file load karne ke liye
load_dotenv()

app = Flask(__name__)
app.secret_key = "DATA_ZONE_PREMIUM_2026"

# Render ke Environment Variable se URL uthayega
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    # sslmode=require hona zaroori hai
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, role, download_limit, download_count, is_active):
        self.id = id
        self.username = username
        self.role = role
        self.download_limit = download_limit
        self.download_count = download_count
        self.is_active = is_active

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['role'], user['download_limit'], user['download_count'], user['is_active'])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        conn.close()
        
        if user:
            user_obj = User(user['id'], user['username'], user['role'], user['download_limit'], user['download_count'], user['is_active'])
            login_user(user_obj)
            return redirect(url_for('index'))
        
        flash('Invalid login!')
    return render_template('login.html')

@app.route('/')
@login_required
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
