from flask import request, render_template, flash, redirect, url_for, Blueprint
from admin.database.firebase import Database

db = Database()
mess_bp = Blueprint('mess',
                         __name__,
                         template_folder="../templates",
                         static_folder="static",
                         static_url_path="/admin_static")

class MessRoutes:
    
    @mess_bp.route('/save_menu', methods=['POST'])
    def save_menu():
        week_menu = {}

        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        for day in days:
            week_menu[day] = {
                "breakfast": request.form.get(f"{day}_breakfast"),
                "lunch": request.form.get(f"{day}_lunch"),
                "dinner": request.form.get(f"{day}_dinner")
            }
        
        db.save_mess_menu(week_menu)

        return redirect(url_for('dashboard.manage_mess'))
    
