from flask import request, render_template, flash, redirect, url_for, Blueprint, send_file
from admin.database.firebase import Database
from datetime import date

db = Database()
fee_bp = Blueprint('fee',
                  __name__,
                  template_folder="../templates")

class FeeRoutes:
    
    @staticmethod
    @fee_bp.route('/fees')
    def view_fees():
        page = int(request.args.get('page', 1))
        per_page = 10
        
        all_data = db.get_all_fees()
        
        total_pages = (len(all_data) + per_page - 1) // per_page
        
        start = (page - 1) * per_page
        end = start + per_page
        data = all_data[start:end]
        
        return render_template('fees.html',
                             data=data,
                             page=page,
                             total_pages=total_pages)
    
    @staticmethod
    @fee_bp.route('/add_fee', methods=['GET', 'POST'])
    def add_fee():
        if request.method == 'POST':
            student_id = request.form.get('student_id')
            amount = request.form.get('amount')
            due_date = request.form.get('due_date')
            fee_type = request.form.get('fee_type')
            
            if not student_id or not amount or not due_date or not fee_type:
                flash("All fields are required", "error")
                return redirect(url_for('fee.add_fee'))
            
            db.add_fee_record(student_id, amount, due_date, fee_type)
            flash("Fee record added successfully", "success")
            return redirect(url_for('fee.view_fees'))
        
        # Get all students for dropdown
        students = db.get_tenants_details()
        
        return render_template('add_fee.html', students=students)
    
    @staticmethod
    @fee_bp.route('/update_payment/<fee_id>', methods=['GET', 'POST'])
    def update_payment(fee_id):
        if request.method == 'POST':
            paid_amount = request.form.get('paid_amount')
            paid_date = request.form.get('paid_date')
            payment_method = request.form.get('payment_method')
            transaction_id = request.form.get('transaction_id')
            notes = request.form.get('notes')
            
            if not paid_amount or not paid_date or not payment_method:
                flash("All required fields must be filled", "error")
                return redirect(url_for('fee.update_payment', fee_id=fee_id))
            
            db.update_fee_payment(fee_id, paid_amount, paid_date, payment_method, transaction_id, notes)
            flash("Payment updated successfully", "success")
            return redirect(url_for('fee.view_fees'))
        
        # GET request - show the update form
        fee_data = db.get_fee_by_id(fee_id)
        if not fee_data:
            flash("Fee record not found", "error")
            return redirect(url_for('fee.view_fees'))
        
        today = date.today().isoformat()
        return render_template('update_payment.html', fee_data=fee_data, today=today)
    
    @staticmethod
    @fee_bp.route('/export_fees')
    def export_fees():
        output = db.export_fees_to_excel()
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'fees_{date.today()}.xlsx'
        )
    
    @staticmethod
    @fee_bp.route('/payment_history/<fee_id>')
    def payment_history(fee_id):
        """View payment history for a specific fee"""
        fee_data = db.get_fee_by_id(fee_id)
        if not fee_data:
            flash("Fee record not found", "error")
            return redirect(url_for('fee.view_fees'))
        
        payments = db.get_payment_history(fee_id=fee_id)
        
        return render_template('payment_history.html', fee_data=fee_data, payments=payments)
