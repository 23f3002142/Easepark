
from flask import Blueprint,render_template,flash,request,url_for,abort,redirect
from flask_login import login_required,current_user
from models.user_model import Users,ParkingLot,ParkingSpot,db

user_blueprint=Blueprint('user',__name__,url_prefix='/dashboard')

@user_blueprint.route('/user')
@login_required
def dashboard():
    if current_user.role != 'user':
        return "Unauthorised"
    else :
        return render_template('user_dashboard.html')
    
@user_blueprint.route('/profile/view')
@login_required
def user_profile_view():
    if current_user.role != 'user':
        abort(404)
    
    return render_template('user_profile_view.html',user=current_user)


@user_blueprint.route('/profile/edit', methods=['GET','POST'])
@login_required
def user_profile_edit():
    if current_user.role != 'user':
        abort(404)
    user=current_user

    if request.method == 'POST':
        if request.method == 'POST':
            user.full_name = request.form['full_name']
            user.username = request.form['username']
            user.email = request.form['email']
            user.phone_number = request.form['phone_number']
            user.address = request.form['address']
            user.pin_code = request.form['pin_code']
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('user.user_profile_view'))
    return render_template('user_profile_edit.html',user=user)