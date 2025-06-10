
from flask import Blueprint,render_template
from flask_login import login_required,current_user

user_blueprint=Blueprint('user',__name__,url_prefix='/dashboard')

@user_blueprint.route('/user')
@login_required
def dashboard():
    if current_user.role != 'user':
        return "Unauthorised"
    else :
        return render_template('user_dashboard.html')
    
