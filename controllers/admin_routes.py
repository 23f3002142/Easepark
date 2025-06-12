
from flask import Blueprint,render_template,redirect,url_for,flash , request , abort
from flask_login import login_required,current_user
from models.user_model import ParkingLot,ParkingSpot,db

admin_blueprint=Blueprint('admin',__name__,url_prefix='/dashboard')

@admin_blueprint.route('/admin')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return "Unauthorised"
    else :
        lots= ParkingLot.query.all()
        return render_template('admin_dashboard.html',Parking_lots=lots)

 # adding a new parking lot
@admin_blueprint.route('/addlot' , methods=['GET','POST'])
def add_lot():
    if request.method=='POST':
        name = request.form['location_name']
        price = request.form['price']
        address = request.form['address']
        pin_code = request.form['pin_code']
        max_spots = request.form['max_spots']

        new_lot= ParkingLot(location_name=name,price=price,address=address,pin_code=pin_code,max_spots=max_spots ) #type: ignore
        db.session.add(new_lot)
        db.session.commit()
        flash('A new Lot is Added', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('add_lot.html')

# Edit parking lot
@admin_blueprint.route('/editlot/<int:lot_id>' , methods=['GET','POST'])
def edit_lot(lot_id):
    lot=ParkingLot.query.filter_by(id=lot_id).first()
    if lot is None:
        abort(404)
    if request.method=='POST':
        lot.location_name = request.form['location_name']
        lot.price = request.form['price']
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        lot.max_spots = request.form['max_spots']

        
        db.session.commit()
        flash('Lot edited Successfully', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('edit_lot.html' , lot=lot)


# deleting parking lots
@admin_blueprint.route('/deletelot/<int:lot_id>')
def delete_lot(lot_id):
    lot=ParkingLot.query.filter_by(id=lot_id).first()
    if lot is None:
        abort(404)
    db.session.delete(lot)
    db.session.commit()
    flash('Parking lot is deleted','danger')
    return redirect(url_for('admin.dashboard'))