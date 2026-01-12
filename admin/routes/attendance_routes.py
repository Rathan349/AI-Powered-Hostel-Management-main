from flask import request, render_template, flash, redirect, url_for, Blueprint, send_file, jsonify, session
from admin.database.firebase import Database
from datetime import date, datetime, timedelta
import json

db = Database()
attendance_bp = Blueprint('attendance',
                         __name__,
                         template_folder="../templates")

class AttendanceRoutes:
    
    @staticmethod
    @attendance_bp.route('/smart_attendance')
    def smart_attendance():
        """Smart attendance dashboard with analytics"""
        if 'username' not in session:
            return redirect(url_for('auth.signin_page'))
        
        try:
            today = date.today()
            tenants = db.get_tenants_details()
            total_students = len(tenants)
            
            today_attendance = db.get_attendance_by_date(str(today))
            
            present_count = len([a for a in today_attendance if a.get('status') == 'Present'])
            absent_count = len([a for a in today_attendance if a.get('status') == 'Absent'])
            leave_count = len([a for a in today_attendance if a.get('status') == 'Leave'])
            not_marked = total_students - len(today_attendance)
            
            present_percentage = (present_count / total_students * 100) if total_students > 0 else 0
            absent_percentage = (absent_count / total_students * 100) if total_students > 0 else 0
            
            weekly_data = AttendanceRoutes._get_weekly_attendance_data()
            trends = AttendanceRoutes._get_attendance_trends()
            poor_attendance = AttendanceRoutes._get_poor_attendance_students()
            recent_records = AttendanceRoutes._get_recent_attendance_records()
            
            return render_template('smart_attendance.html',
                                 total_students=total_students,
                                 present_count=present_count,
                                 absent_count=absent_count,
                                 leave_count=leave_count,
                                 not_marked=not_marked,
                                 present_percentage=round(present_percentage, 1),
                                 absent_percentage=round(absent_percentage, 1),
                                 weekly_data=json.dumps(weekly_data),
                                 trends=trends,
                                 poor_attendance=poor_attendance,
                                 recent_records=recent_records,
                                 current_date=str(today))
        except Exception as e:
            flash(f'Error loading smart attendance: {str(e)}', 'error')
            return redirect(url_for('dashboard.mainpage'))
    
    @staticmethod
    @attendance_bp.route('/attendance')
    def view_attendance():
        """View attendance records with pagination"""
        if 'username' not in session:
            return redirect(url_for('auth.signin_page'))
        
        page = int(request.args.get('page', 1))
        per_page = 20
        date_filter = request.args.get('date', '')
        
        if date_filter:
            all_data = db.get_attendance_by_date(date_filter)
        else:
            all_data = db.get_all_attendance()
        
        # Add student names to attendance records
        for record in all_data:
            try:
                tenant_data = db.get_tenant_s_details(record.get('tenant_id'))
                if tenant_data:
                    record['student_name'] = tenant_data.get('name', 'Unknown')
                    record['room_number'] = tenant_data.get('room', 'N/A')
                else:
                    record['student_name'] = 'Unknown'
                    record['room_number'] = 'N/A'
            except:
                record['student_name'] = 'Unknown'
                record['room_number'] = 'N/A'
        
        total_pages = (len(all_data) + per_page - 1) // per_page
        
        start = (page - 1) * per_page
        end = start + per_page
        data = all_data[start:end]
        
        return render_template('attendance.html',
                             data=data,
                             page=page,
                             total_pages=total_pages,
                             date_filter=date_filter,
                             current_date=str(date.today()))
    
    @staticmethod
    @attendance_bp.route('/mark_attendance', methods=['GET', 'POST'])
    def mark_attendance():
        if 'username' not in session:
            return redirect(url_for('auth.signin_page'))
        
        if request.method == 'POST':
            if request.is_json:
                data = request.json
                attendance_data = data.get('attendance', [])
                attendance_date = data.get('date', str(date.today()))
                
                success_count = 0
                for record in attendance_data:
                    try:
                        tenant_id = record.get('tenant_id')
                        status = record.get('status')
                        
                        if tenant_id and status:
                            db.mark_attendance(int(tenant_id), attendance_date, status)
                            success_count += 1
                    except Exception as e:
                        print(f"Error marking attendance: {e}")
                        continue
                
                return jsonify({
                    'success': True,
                    'message': f'Successfully marked attendance for {success_count} students on {attendance_date}'
                })
            else:
                student_id = request.form.get('student_id')
                attendance_date = request.form.get('date')
                status = request.form.get('status')
                
                if not student_id or not attendance_date or not status:
                    flash("All fields are required", "error")
                    return redirect(url_for('attendance.mark_attendance'))
                
                db.mark_attendance(int(student_id), attendance_date, status)
                flash("Attendance marked successfully", "success")
                return redirect(url_for('attendance.mark_attendance'))
        
        # GET request - get date from query parameter or use today
        selected_date_str = request.args.get('date', str(date.today()))
        
        # Validate date format
        try:
            selected_date_obj = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except:
            selected_date_obj = date.today()
            selected_date_str = str(selected_date_obj)
        
        tenants = db.get_tenants_details()
        selected_attendance = db.get_attendance_by_date(selected_date_str)
        attendance_dict = {a.get('tenant_id'): a.get('status') for a in selected_attendance}
        
        tenant_list = []
        for tenant in tenants:
            tenant_list.append({
                'id': tenant[0],
                'name': tenant[1],
                'room_number': tenant[2],
                'type': tenant[3],
                'current_status': attendance_dict.get(tenant[0], 'Not Marked')
            })
        
        return render_template('mark_attendance.html', 
                             tenants=tenant_list,
                             selected_date=selected_date_str,
                             current_date=str(date.today()))
    
    @staticmethod
    def _get_weekly_attendance_data():
        """Get attendance data for the last 7 days"""
        weekly_data = []
        for i in range(6, -1, -1):
            date_obj = date.today() - timedelta(days=i)
            date_str = str(date_obj)
            
            attendance = db.get_attendance_by_date(date_str)
            present = len([a for a in attendance if a.get('status') == 'Present'])
            absent = len([a for a in attendance if a.get('status') == 'Absent'])
            
            weekly_data.append({
                'date': date_obj.strftime('%m/%d'),
                'present': present,
                'absent': absent
            })
        
        return weekly_data
    
    @staticmethod
    def _get_attendance_trends():
        """Get attendance trends and insights"""
        try:
            trends = []
            total_days = 0
            total_present = 0
            
            for i in range(30):
                date_obj = date.today() - timedelta(days=i)
                attendance = db.get_attendance_by_date(str(date_obj))
                
                if attendance:
                    present = len([a for a in attendance if a.get('status') == 'Present'])
                    total_present += present
                    total_days += 1
            
            avg_attendance = (total_present / total_days) if total_days > 0 else 0
            
            insights = []
            if avg_attendance > 85:
                insights.append("📈 Excellent attendance rate!")
            elif avg_attendance > 70:
                insights.append("📊 Good attendance rate")
            else:
                insights.append("📉 Attendance needs improvement")
            
            today_attendance = db.get_attendance_by_date(str(date.today()))
            yesterday_attendance = db.get_attendance_by_date(str(date.today() - timedelta(days=1)))
            
            today_present = len([a for a in today_attendance if a.get('status') == 'Present'])
            yesterday_present = len([a for a in yesterday_attendance if a.get('status') == 'Present'])
            
            if today_present > yesterday_present:
                insights.append("⬆️ Attendance improved from yesterday")
            elif today_present < yesterday_present:
                insights.append("⬇️ Attendance decreased from yesterday")
            
            return {
                'avg_attendance': round(avg_attendance, 1),
                'insights': insights
            }
        except:
            return {'avg_attendance': 0, 'insights': []}
    
    @staticmethod
    def _get_poor_attendance_students():
        """Get students with poor attendance (less than 70%)"""
        try:
            tenants = db.get_tenants_details()
            poor_attendance = []
            
            for tenant in tenants:
                tenant_id = tenant[0]
                tenant_name = tenant[1]
                tenant_room = tenant[2]
                
                total_days = 0
                present_days = 0
                
                for i in range(30):
                    date_obj = date.today() - timedelta(days=i)
                    attendance = db.get_attendance_by_date(str(date_obj))
                    
                    student_record = next((a for a in attendance if a.get('tenant_id') == tenant_id), None)
                    if student_record:
                        total_days += 1
                        if student_record.get('status') == 'Present':
                            present_days += 1
                
                if total_days > 0:
                    attendance_rate = (present_days / total_days) * 100
                    if attendance_rate < 70:
                        poor_attendance.append({
                            'name': tenant_name,
                            'id': tenant_id,
                            'room': tenant_room,
                            'attendance_rate': round(attendance_rate, 1),
                            'present_days': present_days,
                            'total_days': total_days
                        })
            
            poor_attendance.sort(key=lambda x: x['attendance_rate'])
            return poor_attendance[:10]
        except Exception as e:
            print(f"Error in _get_poor_attendance_students: {e}")
            return []
    
    @staticmethod
    def _get_recent_attendance_records():
        """Get recent attendance records with student details"""
        try:
            recent_records = []
            tenants = db.get_tenants_details()
            tenant_dict = {tenant[0]: {'name': tenant[1], 'room': tenant[2]} for tenant in tenants}
            
            for i in range(3):
                date_obj = date.today() - timedelta(days=i)
                attendance = db.get_attendance_by_date(str(date_obj))
                
                for record in attendance:
                    tenant_id = record.get('tenant_id')
                    if tenant_id in tenant_dict:
                        recent_records.append({
                            'date': date_obj.strftime('%Y-%m-%d'),
                            'student_name': tenant_dict[tenant_id]['name'],
                            'student_id': tenant_id,
                            'room': tenant_dict[tenant_id]['room'],
                            'status': record.get('status'),
                            'time': record.get('time', 'N/A')
                        })
            
            recent_records.sort(key=lambda x: x['date'], reverse=True)
            return recent_records[:20]
        except Exception as e:
            print(f"Error in _get_recent_attendance_records: {e}")
            return []
    
    @staticmethod
    @attendance_bp.route('/api/attendance_stats')
    def get_attendance_stats():
        """API endpoint for real-time attendance statistics"""
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized', 'redirect': url_for('auth.signin_page')}), 401
        
        try:
            today = str(date.today())
            tenants = db.get_tenants_details()
            today_attendance = db.get_attendance_by_date(today)
            
            total_students = len(tenants)
            present_count = len([a for a in today_attendance if a.get('status') == 'Present'])
            absent_count = len([a for a in today_attendance if a.get('status') == 'Absent'])
            leave_count = len([a for a in today_attendance if a.get('status') == 'Leave'])
            not_marked = total_students - len(today_attendance)
            
            return jsonify({
                'total_students': total_students,
                'present': present_count,
                'absent': absent_count,
                'leave': leave_count,
                'not_marked': not_marked,
                'present_percentage': round((present_count / total_students * 100) if total_students > 0 else 0, 1)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @staticmethod
    @attendance_bp.route('/export_attendance')
    def export_attendance():
        output = db.export_attendance_to_excel()
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'attendance_{date.today()}.xlsx'
        )
