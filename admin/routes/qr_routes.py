from flask import request, render_template, flash, redirect, url_for, Blueprint, session, jsonify
from admin.database.firebase import Database
from utils.qr_utils import qr_generator
from datetime import datetime, timedelta
import json

db = Database()
qr_bp = Blueprint('qr',
                  __name__,
                  template_folder="../templates")

class QRRoutes:
    
    @staticmethod
    @qr_bp.route('/digital_documents')
    def digital_documents():
        """Main digital documents dashboard"""
        if 'username' not in session:
            return redirect(url_for('auth.signin_page'))
        
        # Get statistics
        total_students = db.count_tenants()
        active_visitors = 5  # This would come from visitor database
        active_leaves = 3    # This would come from leave database
        
        return render_template('digital_documents.html',
                             total_students=total_students,
                             active_visitors=active_visitors,
                             active_leaves=active_leaves)
    
    @staticmethod
    @qr_bp.route('/student_id_generator')
    def student_id_generator():
        """Student ID QR code generator page"""
        if 'username' not in session:
            return redirect(url_for('auth.signin_page'))
        
        students = db.get_tenants_details()
        return render_template('student_id_generator.html', students=students)
    
    @staticmethod
    @qr_bp.route('/generate_student_qr/<student_id>')
    def generate_student_qr(student_id):
        """Generate QR code for specific student"""
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        try:
            student_data = db.get_tenant_s_details(student_id)
            if not student_data:
                return jsonify({'error': 'Student not found'}), 404
            
            # Add tenant_id to student_data
            student_data['tenant_id'] = student_id
            
            qr_code = qr_generator.generate_student_id_qr(student_data)
            if qr_code:
                return jsonify({
                    'success': True,
                    'qr_code': qr_code,
                    'student_data': student_data
                })
            else:
                return jsonify({'error': 'Failed to generate QR code'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    @qr_bp.route('/visitor_management')
    def visitor_management():
        """Visitor management page"""
        if 'username' not in session:
            return redirect(url_for('auth.signin_page'))
        
        # Get pending and all visitor requests
        pending_requests = db.get_pending_visitor_requests()
        all_requests = db.get_all_visitor_requests()
        
        return render_template('visitor_management.html', 
                             pending_requests=pending_requests,
                             all_requests=all_requests)
    
    @staticmethod
    @qr_bp.route('/register_visitor', methods=['POST'])
    def register_visitor():
        """Register new visitor and generate QR code"""
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        try:
            visitor_data = {
                'visitor_id': f"V{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'name': request.json.get('name'),
                'phone': request.json.get('phone'),
                'visiting_student': request.json.get('visiting_student'),
                'visiting_room': request.json.get('visiting_room'),
                'purpose': request.json.get('purpose', 'Visit'),
                'entry_time': datetime.now().isoformat(),
                'valid_until': (datetime.now() + timedelta(hours=8)).isoformat(),
                'approved_by': session.get('username', 'Admin')
            }
            
            qr_code = qr_generator.generate_visitor_entry_qr(visitor_data)
            if qr_code:
                # In a real system, save visitor data to database
                return jsonify({
                    'success': True,
                    'qr_code': qr_code,
                    'visitor_data': visitor_data
                })
            else:
                return jsonify({'error': 'Failed to generate visitor QR code'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    @qr_bp.route('/leave_management')
    def leave_management():
        """Leave pass management page"""
        if 'username' not in session:
            return redirect(url_for('auth.signin_page'))
        
        # Get pending and all leave requests
        pending_requests = db.get_pending_leave_requests()
        all_requests = db.get_all_leave_requests()
        
        return render_template('leave_management.html', 
                             pending_requests=pending_requests,
                             all_requests=all_requests)
    
    @staticmethod
    @qr_bp.route('/generate_leave_pass', methods=['POST'])
    def generate_leave_pass():
        """Generate digital leave pass with QR code"""
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        try:
            leave_data = {
                'pass_id': f"L{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'student_id': request.json.get('student_id'),
                'student_name': request.json.get('student_name'),
                'room': request.json.get('room'),
                'leave_from': request.json.get('leave_from'),
                'leave_to': request.json.get('leave_to'),
                'purpose': request.json.get('purpose'),
                'destination': request.json.get('destination'),
                'emergency_contact': request.json.get('emergency_contact'),
                'approved_by': session.get('username', 'Admin')
            }
            
            qr_code = qr_generator.generate_leave_pass_qr(leave_data)
            if qr_code:
                # In a real system, save leave data to database
                return jsonify({
                    'success': True,
                    'qr_code': qr_code,
                    'leave_data': leave_data
                })
            else:
                return jsonify({'error': 'Failed to generate leave pass QR code'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    @qr_bp.route('/scan_qr', methods=['POST'])
    def scan_qr():
        """Scan and verify QR code"""
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        try:
            qr_data = request.json.get('qr_data')
            verification_result = qr_generator.verify_qr_code(qr_data)
            
            return jsonify(verification_result)
        except Exception as e:
            return jsonify({'valid': False, 'error': str(e)}), 500
    
    @staticmethod
    @qr_bp.route('/qr_scanner')
    def qr_scanner():
        """QR code scanner page"""
        if 'username' not in session:
            return redirect(url_for('auth.signin_page'))
        
        return render_template('qr_scanner.html')
    
    @staticmethod
    @qr_bp.route('/approve_leave_request/<request_id>', methods=['POST'])
    def approve_leave_request(request_id):
        """Approve a leave request and generate QR code"""
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        try:
            admin_id = session.get('username', 'admin')
            success, result = db.approve_leave_request(request_id, admin_id)
            
            if success:
                # Get the updated request data
                request_data = db.get_leave_request_by_id(request_id)
                if request_data:
                    # Generate QR code
                    leave_data = {
                        'pass_id': result,  # This is the pass_id returned from approval
                        'student_id': request_data['student_id'],
                        'student_name': request_data['student_name'],
                        'room': request_data['room'],
                        'leave_from': request_data['leave_from'],
                        'leave_to': request_data['leave_to'],
                        'purpose': request_data['purpose'],
                        'destination': request_data['destination'],
                        'emergency_contact': request_data['emergency_contact'],
                        'approved_by': admin_id
                    }
                    
                    qr_code = qr_generator.generate_leave_pass_qr(leave_data)
                    
                    # Update the request with QR code
                    if qr_code:
                        doc_ref = db.db.collection("leave_requests").document(request_id)
                        doc_ref.update({'qr_code': qr_code})
                    
                    return jsonify({
                        'success': True,
                        'message': 'Leave request approved successfully',
                        'qr_code': qr_code,
                        'leave_data': leave_data
                    })
            
            return jsonify({'success': False, 'error': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @staticmethod
    @qr_bp.route('/reject_leave_request/<request_id>', methods=['POST'])
    def reject_leave_request(request_id):
        """Reject a leave request"""
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        try:
            admin_id = session.get('username', 'admin')
            reason = request.json.get('reason', 'No reason provided')
            
            success = db.reject_leave_request(request_id, admin_id, reason)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Leave request rejected successfully'
                })
            
            return jsonify({'success': False, 'error': 'Failed to reject request'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @staticmethod
    @qr_bp.route('/approve_visitor_request/<request_id>', methods=['POST'])
    def approve_visitor_request(request_id):
        """Approve a visitor request and generate QR code"""
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        try:
            admin_id = session.get('username', 'admin')
            success, result = db.approve_visitor_request(request_id, admin_id)
            
            if success:
                # Get the updated request data
                request_data = db.get_visitor_request_by_id(request_id)
                if request_data:
                    # Generate QR code
                    visitor_data = {
                        'visitor_id': result,  # This is the visitor_id returned from approval
                        'name': request_data['visitor_name'],
                        'phone': request_data['visitor_phone'],
                        'visiting_student': request_data['student_name'],
                        'visiting_room': request_data['room'],
                        'purpose': request_data['purpose'],
                        'visit_date': request_data['visit_date'],
                        'entry_time': request_data['entry_time'],
                        'valid_until': request_data['valid_until'],
                        'approved_by': admin_id
                    }
                    
                    qr_code = qr_generator.generate_visitor_entry_qr(visitor_data)
                    
                    # Update the request with QR code
                    if qr_code:
                        doc_ref = db.db.collection("visitor_requests").document(request_id)
                        doc_ref.update({'qr_code': qr_code})
                    
                    return jsonify({
                        'success': True,
                        'message': 'Visitor request approved successfully',
                        'qr_code': qr_code,
                        'visitor_data': visitor_data
                    })
            
            return jsonify({'success': False, 'error': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @staticmethod
    @qr_bp.route('/reject_visitor_request/<request_id>', methods=['POST'])
    def reject_visitor_request(request_id):
        """Reject a visitor request"""
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        try:
            admin_id = session.get('username', 'admin')
            reason = request.json.get('reason', 'No reason provided')
            
            success = db.reject_visitor_request(request_id, admin_id, reason)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Visitor request rejected successfully'
                })
            
            return jsonify({'success': False, 'error': 'Failed to reject request'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
