from flask import request, render_template, flash, redirect, url_for, Blueprint, session
from admin.database.firebase import Database

db = Database()
tenant_bp = Blueprint('tenant',
                      __name__,
                      template_folder="../templates",
                      static_folder="static",
                      static_url_path="/admin_static")

class TenantRoutes:
    
    @staticmethod
    @tenant_bp.route('/registertenant')
    def register_tenant():
        room_names = db.get_rooms()
        return render_template('register.html', room_names = room_names)
    
    @staticmethod
    @tenant_bp.route('/registertenant/adding', methods=['POST'])
    def adding_tenant():
        id = request.form.get('idproof')
        name = request.form.get('name')
        t_type = request.form.get('ten-type')
        email = request.form.get('email')
        phone = request.form.get('phone')
        date = request.form.get('movein')
        ac = request.form.get('ac')
        sleep = request.form.get('sleeptime')
        smoking = request.form.get('smoking')
        room = request.form.get('room')
        status = request.form.get('status')
        
        if not id or not name or not t_type or not email or not phone or not room or not date or not ac or not sleep or not smoking or not status:
            flash("All fields are required", "error")
            return render_template('register.html')
        
        if room == "--Select Room--":
            flash("Please select valid room", "error")
            return render_template('register.html')
                
        db.add_tenant(id, name, t_type, email, phone, date, ac, sleep, smoking, room, status)
        flash("Tenant added successfully", "success")
        return redirect(url_for('tenant.register_tenant'))
    
    @staticmethod
    @tenant_bp.route('/delete/<tenant_id>', methods=['POST'])
    def delete_tenant(tenant_id):
        if 'username' not in session:
            flash("Please login to perform this action", "error")
            return redirect(url_for('auth.signin_page'))
        
        try:
            result = db.delete_document("tenants", "id", int(tenant_id))
            if result:
                flash("Student deleted successfully", "success")
            else:
                flash("Error deleting student", "error")
        except Exception as e:
            flash("Error deleting student", "error")
            print(f"Delete error: {e}")
        
        return redirect(url_for('dashboard.manage_tenants'))
    
    @staticmethod
    @tenant_bp.route('/ViewTenants/<ten_id>')
    def view_tenants(ten_id):
        
        data = db.get_tenants_details(ten_id, True)
        return render_template('tenant_details.html',
                               data=data)
    
    @staticmethod
    @tenant_bp.route('/edit/<ten_id>', methods=['GET'])
    def edit_tenant(ten_id):
        ten_data = db.get_tenants_details(ten_id, True)
        room_names = db.get_rooms()
        
        return render_template(
            "register.html",
            mode="edit",
            ten_id=ten_id,
            ten_data=ten_data,
            room_names=room_names
        )
        
    
    @staticmethod
    @tenant_bp.route('edit/<ten_id>/update', methods=['POST'])
    def update_tenant(ten_id):
        ten_id = request.form.get('idproof')
        name = request.form.get('name')
        t_type = request.form.get('ten-type')
        email = request.form.get('email')
        phone = request.form.get('phone')
        date = request.form.get('movein')
        ac = request.form.get('ac')
        sleep = request.form.get('sleeptime')
        smoking = request.form.get('smoking')
        room = request.form.get('room')
        status = request.form.get('status')
        
        if not ten_id or not name or not t_type or not email or not phone or not room or not date or not ac or not sleep or not smoking or not status:
            flash("All fields are required", "error")
            return render_template('register.html')
        
        if room == "--Select Room--":
            flash("Please select valid room", "error")
            return render_template('register.html')
        
        db.update_tenant(ten_id, name, t_type, email, phone, date, ac, sleep, smoking, room, status)
        flash("Tenant updated successfully", "success")
        return redirect(url_for('tenant.register_tenant'))
        
        