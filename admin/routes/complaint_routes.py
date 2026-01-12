from flask import request, redirect, url_for, Blueprint
from admin.database.firebase import Database

db = Database()
complaint_bp = Blueprint('complaint',
                         __name__,
                         template_folder="../templates",
                         )

class ComplaintRoutes:
    
    @staticmethod
    @complaint_bp.route('/solve', methods=['POST'])
    def mark_complaint_solved():
        comp_id = request.form.get("complaint_id")
        
        print(comp_id)
        
        db.update_complaint_status(comp_id)
        
        return redirect(url_for('dashboard.manage_complaints'))
        
        