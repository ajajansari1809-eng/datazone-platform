import os
import psycopg2
from psycopg2.extras import DictCursor
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = "DATA_ZONE_PREMIUM_2026"

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, role, credits, active_status):
        self.id = id
        self.username = username
        self.role = role
        self.credits = credits
        # 'active_status' variable store karega, is_active sirf property hogi
        self.active_status = active_status
    
    @property
    def is_active(self):
        return self.active_status

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT id, username, role, credits, is_active FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    conn.close()
    return User(user['id'], user['username'], user['role'], user['credits'], user['is_active']) if user else None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db()
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        conn.close()
        
        if user:
            # Sahi variable pass kar rahe hain
            user_obj = User(user['id'], user['username'], user['role'], user['credits'], user['is_active'])
            login_user(user_obj)
            return redirect(url_for('index'))
        flash('Invalid Username or Password!')
    return render_template('login.html')

@app.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user)

@app.route('/download/<file_id>')
@login_required
def download_file(file_id):
    if current_user.credits >= 1:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET credits = credits - 1 WHERE id = %s", (current_user.id,))
        conn.commit()
        conn.close()
        return f"File {file_id} downloaded! Credits remaining: {current_user.credits - 1}"
    return "Insufficient credits! Please upgrade your plan."

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
    
