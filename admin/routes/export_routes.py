from flask import Blueprint, send_file
from admin.database.firebase import Database
from datetime import date

db = Database()
export_bp = Blueprint('export',
                     __name__,
                     template_folder="../templates")

class ExportRoutes:
    
    @staticmethod
    @export_bp.route('/export_students_csv')
    def export_students_csv():
        output = db.export_students_to_csv()
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'students_{date.today()}.csv'
        )
    
    @staticmethod
    @export_bp.route('/export_students_excel')
    def export_students_excel():
        output = db.export_students_to_excel()
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'students_{date.today()}.xlsx'
        )
