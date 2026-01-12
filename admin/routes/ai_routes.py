from flask import request, render_template, flash, redirect, url_for, Blueprint, jsonify
from admin.database.firebase import Database
from utils.ml_utils import predict_priority, extract_features

db = Database()
ai_bp = Blueprint("ai", 
                  __name__,
                  template_folder="../templates")

class AIRoutes:
    
    @staticmethod
    @ai_bp.route('/dashboard')
    def ai_dashboard():
        """Display AI features dashboard"""
        return render_template('ai_dashboard.html')
    
    @staticmethod
    @ai_bp.route('/predictRoom', methods=['POST'])
    def predict_room():
        """AI-powered room recommendation based on student preferences"""
        data = request.json
        ten_type = data.get('ten_type')
        ac = data.get('ac')
        sleeptime = data.get('sleeptime')
        smoking = data.get('smoking')
        
        # Get available rooms
        available_rooms = db.get_rooms()
        
        if not available_rooms:
            return jsonify({'success': False, 'message': 'No available rooms'})
        
        # Get room details and score them
        room_scores = []
        for room_no in available_rooms:
            room_data = db.get_rooms_details(room_no, edit=True)
            
            # Get current tenants in the room
            tenants = db.db.collection('tenants').where('room', '==', room_no).get()
            
            compatibility_score = 0
            
            # Check AC preference match
            if room_data[3] == ac:  # room_data[3] is AC status
                compatibility_score += 30
            
            # Check compatibility with existing roommates
            for tenant in tenants:
                tenant_data = tenant.to_dict()
                
                # Sleep time compatibility (within 2 hours)
                try:
                    tenant_sleep = int(tenant_data.get('sleep_time', '22'))
                    student_sleep = int(sleeptime)
                    sleep_diff = abs(tenant_sleep - student_sleep)
                    if sleep_diff <= 2:
                        compatibility_score += 25
                    elif sleep_diff <= 4:
                        compatibility_score += 10
                except:
                    pass
                
                # Smoking preference match
                if tenant_data.get('smoking') == smoking:
                    compatibility_score += 25
                
                # Type match (student/working professional)
                if tenant_data.get('type') == ten_type:
                    compatibility_score += 20
            
            room_scores.append({
                'room_no': room_no,
                'score': compatibility_score,
                'floor': room_data[1],
                'capacity': room_data[2],
                'ac': room_data[3],
                'current_occupants': len(tenants)
            })
        
        # Sort by score (highest first)
        room_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top 3 recommendations
        recommendations = room_scores[:3]
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'message': f'Found {len(recommendations)} compatible rooms'
        })
    
    @staticmethod
    @ai_bp.route('/predictComplaintPriority', methods=['POST'])
    def predict_complaint_priority():
        """AI-powered complaint priority prediction"""
        data = request.json
        complaint_text = data.get('complaint_text', '')
        complaint_type = data.get('complaint_type', 'General')
        
        if not complaint_text:
            return jsonify({'success': False, 'message': 'Complaint text is required'})
        
        try:
            # Extract features
            features = extract_features(complaint_text, complaint_type)
            
            # Predict priority
            priority = predict_priority(features)
            
            return jsonify({
                'success': True,
                'priority': priority,
                'message': f'Predicted priority: {priority}'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error predicting priority: {str(e)}'
            })
    
    @staticmethod
    @ai_bp.route('/analyzePaymentRisk', methods=['POST'])
    def analyze_payment_risk():
        """Analyze payment risk for students"""
        data = request.json
        student_id = data.get('student_id')
        
        if not student_id:
            return jsonify({'success': False, 'message': 'Student ID is required'})
        
        try:
            # Get student's payment history
            fees = db.get_student_fees(student_id)
            
            if not fees:
                return jsonify({
                    'success': True,
                    'risk_level': 'Unknown',
                    'message': 'No payment history available'
                })
            
            # Calculate risk factors
            total_fees = len(fees)
            pending_fees = sum(1 for fee in fees if fee.get('status') == 'Pending')
            partial_fees = sum(1 for fee in fees if fee.get('status') == 'Partial')
            paid_fees = sum(1 for fee in fees if fee.get('status') == 'Paid')
            
            # Calculate risk score
            risk_score = 0
            
            if total_fees > 0:
                pending_ratio = pending_fees / total_fees
                partial_ratio = partial_fees / total_fees
                
                risk_score = (pending_ratio * 50) + (partial_ratio * 30)
                
                # Check for overdue payments
                from datetime import datetime
                overdue_count = 0
                for fee in fees:
                    if fee.get('status') in ['Pending', 'Partial']:
                        try:
                            due_date = datetime.fromisoformat(fee.get('due_date'))
                            if due_date < datetime.now():
                                overdue_count += 1
                        except:
                            pass
                
                if overdue_count > 0:
                    risk_score += (overdue_count * 10)
            
            # Determine risk level
            if risk_score >= 60:
                risk_level = 'High'
            elif risk_score >= 30:
                risk_level = 'Medium'
            else:
                risk_level = 'Low'
            
            return jsonify({
                'success': True,
                'risk_level': risk_level,
                'risk_score': round(risk_score, 2),
                'total_fees': total_fees,
                'pending_fees': pending_fees,
                'partial_fees': partial_fees,
                'paid_fees': paid_fees,
                'message': f'Payment risk level: {risk_level}'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error analyzing payment risk: {str(e)}'
            })
    
    @staticmethod
    @ai_bp.route('/forecastMessAttendance', methods=['POST'])
    def forecast_mess_attendance():
        """Forecast mess attendance for planning"""
        try:
            # Get historical mess attendance data
            from datetime import datetime, timedelta
            
            # Get last 7 days of attendance
            attendance_data = []
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).date()
                date_str = str(date)
                
                doc = db.db.collection("messAttendance").document(date_str).get()
                if doc.exists:
                    data = doc.to_dict()
                    attendance_data.append(len(data))
                else:
                    attendance_data.append(0)
            
            if not attendance_data or sum(attendance_data) == 0:
                return jsonify({
                    'success': True,
                    'forecast': 0,
                    'message': 'No historical data available'
                })
            
            # Simple moving average forecast
            avg_attendance = sum(attendance_data) / len(attendance_data)
            
            # Adjust for day of week (weekends typically have lower attendance)
            tomorrow = datetime.now() + timedelta(days=1)
            if tomorrow.weekday() in [5, 6]:  # Saturday or Sunday
                forecast = int(avg_attendance * 0.8)
            else:
                forecast = int(avg_attendance)
            
            return jsonify({
                'success': True,
                'forecast': forecast,
                'average_last_7_days': round(avg_attendance, 1),
                'historical_data': attendance_data,
                'message': f'Forecasted attendance: {forecast} students'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error forecasting attendance: {str(e)}'
            })
    
    @staticmethod
    @ai_bp.route('/suggestRoommate', methods=['POST'])
    def suggest_roommate():
        """Suggest compatible roommates for a student"""
        data = request.json
        student_id = data.get('student_id')
        
        if not student_id:
            return jsonify({'success': False, 'message': 'Student ID is required'})
        
        try:
            # Get student details
            student = db.get_tenant_s_details(student_id)
            
            if not student:
                return jsonify({'success': False, 'message': 'Student not found'})
            
            # Get all students in the same room
            room_no = student.get('room')
            roommates = db.db.collection('tenants').where('room', '==', room_no).get()
            
            compatibility_scores = []
            
            for roommate in roommates:
                roommate_data = roommate.to_dict()
                
                # Skip self
                if roommate_data.get('id') == int(student_id):
                    continue
                
                score = 0
                reasons = []
                
                # Sleep time compatibility
                try:
                    student_sleep = int(student.get('sleep_time', '22'))
                    roommate_sleep = int(roommate_data.get('sleep_time', '22'))
                    sleep_diff = abs(student_sleep - roommate_sleep)
                    
                    if sleep_diff <= 1:
                        score += 30
                        reasons.append('Similar sleep schedule')
                    elif sleep_diff <= 2:
                        score += 20
                except:
                    pass
                
                # Smoking preference
                if student.get('smoking') == roommate_data.get('smoking'):
                    score += 25
                    reasons.append('Same smoking preference')
                
                # Type (student/professional)
                if student.get('type') == roommate_data.get('type'):
                    score += 20
                    reasons.append('Same occupation type')
                
                # AC preference
                if student.get('ac') == roommate_data.get('ac'):
                    score += 15
                    reasons.append('Same AC preference')
                
                compatibility_scores.append({
                    'roommate_id': roommate_data.get('id'),
                    'roommate_name': roommate_data.get('name'),
                    'compatibility_score': score,
                    'reasons': reasons
                })
            
            # Sort by compatibility score
            compatibility_scores.sort(key=lambda x: x['compatibility_score'], reverse=True)
            
            return jsonify({
                'success': True,
                'roommates': compatibility_scores,
                'message': f'Found {len(compatibility_scores)} roommates'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error suggesting roommates: {str(e)}'
            })
    
