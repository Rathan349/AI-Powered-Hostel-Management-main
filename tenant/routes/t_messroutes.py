from flask import request, render_template, flash, redirect, url_for, Blueprint, session
from tenant.database.firebase import Database

db = Database()
t_mess_bp = Blueprint('t_mess',
                      __name__,
                    template_folder="../templates")

class TMessRoutes:
    
    @staticmethod
    @t_mess_bp.route("/saveAttendance", methods=["POST"])
    def save_attendance():
        attendance = request.form.getlist('attendance')
        ten_id = session["tenant_id"]
        
        breakfast = "breakfast" in attendance
        lunch = "lunch" in attendance
        dinner = "dinner" in attendance
        
        db.save_tenant_attendance(ten_id, breakfast, lunch, dinner)
        flash("Attendance marked for today", "success")
        
        return redirect(url_for('t_dashboard.mess_page'))
    
    
    
    
        