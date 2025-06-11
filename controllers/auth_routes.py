from flask import Blueprint, request, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from models.user_model import Users, db


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
                return redirect(url_for('user.dashboard'))
    
    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash('you have logged out')
    return redirect(url_for('auth.login'))