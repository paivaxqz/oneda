from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
import os
import secrets

app = Flask(__name__)
# Security: Use ENV var for production or fallback for dev
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Security Headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# Configuração do Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'

DB_NAME = "database.db"

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    user_data = c.fetchone()
    conn.close()
    if user_data:
        return User(user_data[0], user_data[1])
    return None

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        invite_key = request.form['invite_key']
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Valida Chave
        c.execute("SELECT * FROM invite_keys WHERE key = ? AND is_used = 0", (invite_key,))
        key_data = c.fetchone()
        
        if not key_data:
            flash('Chave de convite inválida ou já usada!', 'error')
            conn.close()
            return redirect(url_for('register'))
            
        # Cria Usuário
        hashed_pw = generate_password_hash(password)
        try:
            c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_pw))
            user_id = c.lastrowid
            
            # Queima a chave
            c.execute("UPDATE invite_keys SET is_used = 1, used_by_user_id = ? WHERE key = ?", (user_id, invite_key))
            
            # Cria entrada inicial do bot
            c.execute("INSERT INTO bots (user_id) VALUES (?)", (user_id,))
            
            conn.commit()
            flash('Conta criada com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Nome de usuário já existe.', 'error')
        finally:
            conn.close()
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = c.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data['id'], user_data['username'])
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos.', 'error')
            
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM bots WHERE user_id = ?", (current_user.id,))
    bot_data = c.fetchone()
    conn.close()
    return render_template('dashboard.html', bot=bot_data)

@app.route('/update_bot', methods=['POST'])
@login_required
def update_bot():
    token = request.form['token']
    categories = request.form['categories']
    message = request.form['message']
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE bots 
        SET discord_token = ?, category_ids = ?, response_msg = ?
        WHERE user_id = ?
    """, (token, categories, message, current_user.id))
    conn.commit()
    conn.close()
    
    flash('Configurações salvas!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/toggle_bot', methods=['POST'])
@login_required
def toggle_bot():
    conn = get_db_connection()
    c = conn.cursor()
    # Pega estado atual
    c.execute("SELECT is_active FROM bots WHERE user_id = ?", (current_user.id,))
    current_state = c.fetchone()['is_active']
    new_state = 0 if current_state else 1
    
    c.execute("UPDATE bots SET is_active = ? WHERE user_id = ?", (new_state, current_user.id))
    conn.commit()
    conn.close()
    
    status = "ON" if new_state else "OFF"
    flash(f'Bot {status}!', 'info')
    return redirect(url_for('dashboard'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    # Security: Require Admin Username/Password via Session
    if not session.get('is_admin'):
        if request.method == 'POST' and 'admin_user' in request.form and 'admin_pass' in request.form:
            env_user = os.environ.get('ADMIN_USERNAME', 'admin')
            env_pass = os.environ.get('ADMIN_PASSWORD', 'admin123')
            
            if request.form['admin_user'] == env_user and request.form['admin_pass'] == env_pass:
                session['is_admin'] = True
                flash('Admin Access Granted', 'success')
                return redirect(url_for('admin'))
            else:
                flash('Invalid Identity', 'error')
        
        # Show Admin Login Form
        return render_template('admin_login.html')

    # PRG Pattern to fix F5 Bug
    if request.method == 'POST' and 'generate' in request.form:
        import secrets
        key = "INVITE-" + secrets.token_hex(4).upper()
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO invite_keys (key) VALUES (?)", (key,))
        conn.commit()
        conn.close()
        flash(f'NEW KEY GENERATED: {key}', 'success')
        return redirect(url_for('admin'))
            
    # List active keys with User info
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT k.*, u.username as used_by
        FROM invite_keys k
        LEFT JOIN users u ON k.used_by_user_id = u.id
        ORDER BY k.created_at DESC LIMIT 20
    """)
    keys = c.fetchall()
    conn.close()
    
    return render_template('admin.html', keys=keys)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
