from flask import request, render_template, flash, redirect, url_for, Blueprint, session
from admin.database.firebase import Database

db = Database()
dashboard_bp = Blueprint('dashboard',
                         __name__,
                         template_folder="../templates")

class DashboardRoutes:
    
    @staticmethod
    @dashboard_bp.route('/dashboard')
    def mainpage():
        if 'username' not in session:
            flash("Please login to access dashboard", "error")
            return redirect(url_for('auth.signin_page'))
        
        tenant_count = db.count_tenants()
        occ_room_count = db.count_rooms(True)
        com_count = db.count_complaints()
        mess_count = db.count_mess()
        
        return render_template('index.html',
                               tenant_count=tenant_count,
                               occupied_rooms=occ_room_count,
                               com_count = com_count,
                               mess_count=mess_count
                               )
    
    @staticmethod
    @dashboard_bp.route('/manage_tenants')
    def manage_tenants():
        if 'username' not in session:
            flash("Please login to access this page", "error")
            return redirect(url_for('auth.signin_page'))
        
        page = int(request.args.get('page', 1))
        per_page = 5
        
        all_data = db.get_tenants_details()
        
        total_pages = (len(all_data) + per_page -1 ) // per_page
        
        start = (page - 1) * per_page
        end = start + per_page
        data = all_data[start:end]
        
        return render_template('manage_tenants.html', 
                               data = data,
                               page = page,
                               total_pages = total_pages
                               )
    
    @staticmethod
    @dashboard_bp.route('/manage_rooms', methods=['GET'])
    def manage_rooms():
        page = int(request.args.get('page', 1))
        per_page = 5
        
        all_data = db.get_rooms_details()
        
        total_pages = (len(all_data) + per_page -1 ) // per_page
        
        start = (page - 1) * per_page
        end = start + per_page
        data = all_data[start:end]
        
        return render_template('manage_rooms.html',
                               data = data,
                               page = page,
                               total_pages = total_pages
                               )

    @staticmethod
    @dashboard_bp.route('/manage_mess')
    def manage_mess():
        page = int(request.args.get('page', 1))
        per_page = 5
        
        all_data = db.get_mess_data()
        
        total_pages = (len(all_data) + per_page -1 ) // per_page
        
        start = (page - 1) * per_page
        end = start + per_page
        data = all_data[start:end]
        
        return render_template('mess.html',
                               data = data,
                               page = page,
                               total_pages = total_pages)

    @staticmethod
    @dashboard_bp.route('/manage_complaints')
    def manage_complaints():
        page = int(request.args.get('page', 1))
        per_page = 5
        
        all_data = db.get_complaint_details()
        
        print(all_data)
                
        total_pages = (len(all_data) + per_page -1 ) // per_page
        
        start = (page - 1) * per_page
        end = start + per_page
        data = all_data[start:end]
        
        return render_template('complaints.html', 
                               data = data,
                               page = page,
                               total_pages = total_pages
                               )
    
    
    
    
    