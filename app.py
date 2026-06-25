from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import psycopg2
from psycopg2.extras import DictCursor
import os

app = Flask(__name__)
app.secret_key = "DATA_ZONE_PREMIUM_2026"
db_url = os.environ.get('DATABASE_URL')

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, role, credits, active):
        self.id = id; self.username = username; self.role = role
        self.credits = credits; self.active = active
    def get_id(self): return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    conn = psycopg2.connect(db_url, sslmode='require')
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    u = cur.fetchone()
    conn.close()
    return User(u['id'], u['username'], u['role'], u['credits'], u['is_active']) if u else None

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Database check logic here
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin': return "Access Denied"
    return render_template('admin.html')

if __name__ == '__main__':
    app.run()
    
