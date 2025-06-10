
from flask import Blueprint,render_template
from flask_login import login_required,current_user

admin_blueprint=Blueprint('admin',__name__,url_prefix='/dashboard')

@admin_blueprint.route('/admin')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return "Unauthorised"
    else :
        return render_template('admin_dashboard.html')
    
