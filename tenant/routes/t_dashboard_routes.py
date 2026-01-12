from flask import request, render_template, flash, redirect, url_for, Blueprint, session
from tenant.database.firebase import Database

db = Database()
t_dashboard_bp = Blueprint('t_dashboard',
                      __name__,
                    template_folder="../templates"
                    )



class TDashboardRoutes:
    
    @t_dashboard_bp.app_context_processor
    def inject_tenant_name():
        ten_id = session.get('tenant_id')
        name = None
        if ten_id:
            name = db.get_tenant_details(ten_id, "name") 
        
        return dict(Tenant_Name = name)
    
    @staticmethod
    @t_dashboard_bp.route('/')
    def dashboard_page():
        return render_template('tenant-dashboard.html')
    
    @staticmethod
    @t_dashboard_bp.route('/profile')
    def profile_page():
      ten_id = session.get('tenant_id')
      tenants = db.get_tenant_details(ten_id)
      return render_template('tenant-profile.html', data=tenants)
    
    @staticmethod
    @t_dashboard_bp.route('/Fullprofile')
    def fullprofile_page():
      ten_id = session.get('tenant_id')
      tenants = db.get_tenant_details(ten_id)
      return render_template('tenant-full-profile.html', data=tenants)
    
    @staticmethod
    @t_dashboard_bp.route('/roomInfo')
    def room_page():
      ten_id = session.get("tenant_id")
      rooms = db.get_room_details(ten_id)
      ten_room = db.get_tenant_details(ten_id, "room")
      tenant_data = db.get_room_tenant_details(ten_id, ten_room)
      return render_template('tenant-room.html', 
                             data=rooms, 
                             tenants=tenant_data)
    
    @staticmethod
    @t_dashboard_bp.route('/mess')
    def mess_page():
      mess_data = db.get_menu_data()
      return render_template('tenant-mess.html', data=mess_data)
    
    @staticmethod
    @t_dashboard_bp.route('/complaints')
    def complaint_page():
      ten_id = session.get("tenant_id")
      complaint_det = db.get_complaint_details(ten_id)
      return render_template('tenant-complaints.html',
                             data=complaint_det)
    
    @staticmethod
    @t_dashboard_bp.route('/complaints')
    def logout():
      session.clear()
      return redirect(url_for('t_auth.signin_page'))
    
    
    
    
    
    
    
    
    
    