import os
import psycopg2
from psycopg2.extras import DictCursor
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = "DATA_ZONE_PREMIUM_2026"

# Render environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')
# Render pe file save karne ke liye /tmp folder ka use karein
UPLOAD_FOLDER = '/tmp' 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, role, download_limit, download_count, active_status):
        self.id = id
        self.username = username
        self.role = role
        self.download_limit = download_limit
        self.download_count = download_count
        self.active_status = active_status
    
    @property
    def is_active(self):
        return self.active_status

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    conn.close()
    return User(user['id'], user['username'], user['role'], user['download_limit'], user['download_count'], user['is_active']) if user else None

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
            user_obj = User(user['id'], user['username'], user['role'], user['download_limit'], user['download_count'], user['is_active'])
            login_user(user_obj)
            return redirect(url_for('index'))
        flash('Invalid username or password!')
    return render_template('login.html')

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files: return "No file part"
    file = request.files['file']
    if file.filename == '': return "No selected file"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return "File uploaded successfully!"

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    new_password = request.form.get('password')
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, current_user.id))
    conn.commit()
    conn.close()
    flash('Password updated successfully!')
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
