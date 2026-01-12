from flask import request, render_template, flash, redirect, url_for, Blueprint, session, jsonify
from tenant.database.firebase import Database
from utils.qr_utils import qr_generator
from datetime import datetime, timedelta
import json

db = Database()
t_qr_bp = Blueprint('t_qr',
                    __name__,
                    template_folder="../templates")

class TQRRoutes:
    
    @staticmethod
    @t_qr_bp.route('/digital_id')
    def digital_id():
        """Student digital ID page"""
        student_id = session.get('tenant_id')
        if not student_id:
            flash("Please login first", "error")
            return redirect(url_for('t_auth.signin_page'))
        
        student_data = db.get_tenant_details(student_id)
        return render_template('student_digital_id.html', 
                             student_data=student_data,
                             student_id=student_id)
    
    @staticmethod
    @t_qr_bp.route('/generate_my_qr')
    def generate_my_qr():
        """Generate QR code for current student"""
        student_id = session.get('tenant_id')
        if not student_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        try:
            student_data = db.get_tenant_details(student_id)
            if not student_data:
                return jsonify({'error': 'Student data not found'}), 404
            
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
    @t_qr_bp.route('/leave_request')
    def leave_request():
        """Student leave request page"""
        student_id = session.get('tenant_id')
        if not student_id:
            flash("Please login first", "error")
            return redirect(url_for('t_auth.signin_page'))
        
        student_data = db.get_tenant_details(student_id)
        
        # Get student's leave history
        leave_history = db.get_my_leave_requests(student_id)
        
        return render_template('student_leave_request.html',
                             student_data=student_data,
                             student_id=student_id,
                             leave_history=leave_history)
    
    @staticmethod
    @t_qr_bp.route('/request_leave', methods=['POST'])
    def request_leave():
        """Submit leave request for admin approval"""
        student_id = session.get('tenant_id')
        if not student_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        try:
            student_data = db.get_tenant_details(student_id)
            
            # Submit leave request to database
            request_id = db.submit_leave_request(
                student_id=student_id,
                student_name=student_data.get('name'),
                room=student_data.get('room'),
                leave_from=request.json.get('leave_from'),
                leave_to=request.json.get('leave_to'),
                purpose=request.json.get('purpose'),
                destination=request.json.get('destination'),
                emergency_contact=request.json.get('emergency_contact')
            )
            
            if request_id:
                return jsonify({
                    'success': True,
                    'request_id': request_id,
                    'message': 'Leave request submitted successfully! Please wait for admin approval.'
                })
            else:
                return jsonify({'error': 'Failed to submit leave request'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    @t_qr_bp.route('/visitor_invite')
    def visitor_invite():
        """Student visitor invitation page"""
        student_id = session.get('tenant_id')
        if not student_id:
            flash("Please login first", "error")
            return redirect(url_for('t_auth.signin_page'))
        
        student_data = db.get_tenant_details(student_id)
        
        # Get visitor history
        visitor_history = db.get_my_visitor_requests(student_id)
        
        return render_template('student_visitor_invite.html',
                             student_data=student_data,
                             student_id=student_id,
                             visitor_history=visitor_history)
    
    @staticmethod
    @t_qr_bp.route('/invite_visitor', methods=['POST'])
    def invite_visitor():
        """Submit visitor invitation request for admin approval"""
        student_id = session.get('tenant_id')
        if not student_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        try:
            student_data = db.get_tenant_details(student_id)
            
            # Submit visitor request to database
            request_id = db.submit_visitor_request(
                student_id=student_id,
                student_name=student_data.get('name'),
                room=student_data.get('room'),
                visitor_name=request.json.get('name'),
                visitor_phone=request.json.get('phone'),
                visit_date=request.json.get('visit_date'),
                entry_time=request.json.get('entry_time'),
                purpose=request.json.get('purpose', 'Visit'),
                valid_until=request.json.get('valid_until')
            )
            
            if request_id:
                return jsonify({
                    'success': True,
                    'request_id': request_id,
                    'message': 'Visitor invitation submitted successfully! Please wait for admin approval.'
                })
            else:
                return jsonify({'error': 'Failed to submit visitor request'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    @t_qr_bp.route('/my_documents')
    def my_documents():
        """Student's digital documents dashboard"""
        student_id = session.get('tenant_id')
        if not student_id:
            flash("Please login first", "error")
            return redirect(url_for('t_auth.signin_page'))
        
        student_data = db.get_tenant_details(student_id)
        
        return render_template('student_documents.html',
                             student_data=student_data,
                             student_id=student_id)
    
    @staticmethod
    @t_qr_bp.route('/qr_scanner')
    def qr_scanner():
        """Student QR code scanner page"""
        student_id = session.get('tenant_id')
        if not student_id:
            flash("Please login first", "error")
            return redirect(url_for('t_auth.signin_page'))
        
        student_data = db.get_tenant_details(student_id)
        
        return render_template('student_qr_scanner.html',
                             student_data=student_data,
                             student_id=student_id)
    
    @staticmethod
    @t_qr_bp.route('/verify_qr', methods=['POST'])
    def verify_qr():
        """Verify QR code for students"""
        student_id = session.get('tenant_id')
        if not student_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        try:
            qr_data = request.json.get('qr_data')
            if not qr_data:
                return jsonify({'valid': False, 'error': 'No QR data provided'})
            
            # Try to parse as JSON first
            try:
                parsed_data = json.loads(qr_data)
                verification_result = qr_generator.verify_qr_code(qr_data)
            except json.JSONDecodeError:
                # If not JSON, treat as raw data
                verification_result = {'valid': False, 'error': 'Invalid QR code format'}
            
            return jsonify(verification_result)
        except Exception as e:
            return jsonify({'valid': False, 'error': str(e)})