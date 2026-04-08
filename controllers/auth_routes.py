from flask import Blueprint, request, render_template, redirect, url_for, flash,session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from models.user_model import Users, db
from extensions import oauth
import base64
import os
auth=Blueprint('auth',__name__)


def _generate_unique_username(seed: str) -> str:
    base = (seed or 'user').strip().lower()
    cleaned = ''.join(ch for ch in base if ch.isalnum() or ch in ['.', '_', '-']).strip('._-')
    if not cleaned:
        cleaned = 'user'

    candidate = cleaned[:80]
    if not Users.query.filter_by(username=candidate).first():
        return candidate

    suffix = 1
    while True:
        suffix_str = str(suffix)
        trimmed = cleaned[: max(1, 80 - len(suffix_str) - 1)]
        candidate = f"{trimmed}_{suffix_str}"
        if not Users.query.filter_by(username=candidate).first():
            return candidate
        suffix += 1

@auth.route("/register", methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form['username']
        email=request.form['email']
        password=request.form['password']
        role = 'user'

        hash_pw=generate_password_hash(password)
        user= Users(username=username, email=email, password=hash_pw, role=role) # type: ignore
        db.session.add(user)
        
        try:
            db.session.commit()
            flash('Registration completed', 'success')
            return redirect(url_for('auth.login'))
        except:
            db.session.rollback()
            flash('Username or email already exists.', 'danger')
    
    return render_template('register1.html')

@auth.route("/login", methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        user=Users.query.filter_by(username=username).first()

        if user and check_password_hash(user.password , password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard',user=user))
    
    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash('you have logged out')
    return redirect(url_for('home'))


#Google auths 
@auth.route('/google-login')
def google_login():
    base_url = os.getenv('BASE_URL', request.host_url.rstrip('/'))
    redirect_uri = f"{base_url}{url_for('auth.google_authorize')}"
    
    nonce = base64.urlsafe_b64encode(os.urandom(16)).decode() # type: ignore
    session['nonce'] = nonce
    return oauth.google.authorize_redirect(redirect_uri, nonce=session['nonce']) # type: ignore

@auth.route('/google-authorize')
def google_authorize():
    try:
        token = oauth.google.authorize_access_token()# type: ignore
        nonce = session.pop('nonce', None)
        user_info = oauth.google.parse_id_token(token, nonce=nonce)# type: ignore
    except Exception:
        flash('Google sign-in failed. Please try again.', 'danger')
        return redirect(url_for('auth.login'))

    email = (user_info.get('email') or '').strip().lower() if user_info else ''
    full_name = (user_info.get('name') or '').strip() if user_info else ''
    if not email:
        flash('Google account email was not provided.', 'danger')
        return redirect(url_for('auth.login'))

    # Find user by email
    user = Users.query.filter_by(email=email).first()

    # creating a new user 
    if not user:
        username_seed = email.split('@')[0]
        if full_name:
            username_seed = username_seed or full_name
        username = _generate_unique_username(username_seed)

        user = Users(
            email=email, # type: ignore
            username=username, # type: ignore
            full_name=full_name or username, # type: ignore
            password=None,  # type: ignore
            role='user' # type: ignore
        )
        db.session.add(user)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash('Could not complete Google sign-in. Please try again.', 'danger')
            return redirect(url_for('auth.login'))
        flash('Account created successfully via Google!', 'success')
    

    login_user(user)
    

    if user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('user.dashboard',user=user))