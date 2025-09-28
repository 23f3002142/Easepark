from flask import Blueprint, request, render_template, redirect, url_for, flash,session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from models.user_model import Users, db
from extensions import oauth
import base64
import os
auth=Blueprint('auth',__name__)

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
    return redirect(url_for('auth.login'))


#Google auths 
@auth.route('/google-login')
def google_login():
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    redirect_uri = f"{base_url}{url_for('auth.google_authorize')}"
    print("Redirecting to Google with redirect_uri:", redirect_uri)
    
    nonce = base64.urlsafe_b64encode(os.urandom(16)).decode() # type: ignore
    session['nonce'] = nonce
    return oauth.google.authorize_redirect(redirect_uri, nonce=session['nonce']) # type: ignore

@auth.route('/google-authorize')
def google_authorize():
    token = oauth.google.authorize_access_token()# type: ignore
    
    nonce = session.pop('nonce', None)
    user_info = oauth.google.parse_id_token(token, nonce=nonce)# type: ignore
    # Find user by email
    user = Users.query.filter_by(email=user_info['email']).first()

    # If user doesn't exist, create a new one
    if not user:
        # Check if username from email already exists
        username = user_info['email'].split('@')[0]
        if Users.query.filter_by(username=username).first():
            username = user_info['name'] # Use full name if username exists

        user = Users(
            email=user_info['email'], # type: ignore
            username=username, # type: ignore
            full_name=user_info['name'], # type: ignore
            password=None,  # type: ignore
            role='user' # type: ignore
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully via Google!', 'success')
    
    # Log in the user
    login_user(user)
    
    # Redirect based on role
    if user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('user.dashboard',user=user))