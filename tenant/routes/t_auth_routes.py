from flask import request, render_template, flash, redirect, url_for, Blueprint, session
from tenant.database.firebase import Database
from datetime import datetime, timedelta
from utils.email_service import EmailService
import random 

db = Database()
t_auth_bp = Blueprint('t_auth',
                      __name__,
                    template_folder="../templates",
                    static_folder="../static",
                    static_url_path="/tenant_static"
                    )
  
class TAuthRoutes:
    
    @staticmethod
    @t_auth_bp.route('/signup')
    def signup_page():
        return render_template('tenant-signup.html')
    
    @staticmethod
    @t_auth_bp.route('/signin')
    def signin_page():
        return render_template('tenant-signin.html')
    
    @staticmethod
    @t_auth_bp.route('/ForgetPass')
    def forget_pass():
        return render_template("tenant-forget-password.html")
    
    @staticmethod
    @t_auth_bp.route('/verify_student', methods=["POST"])
    def verify_student():
        try:
            email = request.form.get('email', '').strip()
            
            if not email:
                flash("Email is required", "error")
                return render_template('tenant-forget-password.html')
            
            # Validate email format
            if not db.validate_email(email):
                flash("Please enter a valid email address", "error")
                return render_template('tenant-forget-password.html')
            
            # Check if email exists in tenants collection
            student_data = db.get_tenant_by_email(email)
            if not student_data:
                flash("Email not found in our records", "error")
                return render_template('tenant-forget-password.html')
            
            student_id = student_data.get('id')
            
            # Check if student has login credentials
            if not db.tenant_has_auth(student_id):
                flash("No account found for this email. Please register first.", "error")
                return render_template('tenant-forget-password.html')
            
            # Generate verification code
            code = str(random.randint(100000, 999999))
            session["verification_code"] = code
            session['email_code_expiry'] = (datetime.now() + timedelta(minutes=5)).timestamp()
            session["student_id"] = student_id
            session["student_email"] = email
            
            # Send email using EmailService
            success, message = EmailService.send_verification_code(
                email, 
                code, 
                student_data.get('name', 'Student')
            )
            
            if success:
                flash("Verification code sent to your email", "success")
                return render_template("tenant-verify-code.html")
            else:
                flash(f"Error sending email: {message}", "error")
                return render_template('tenant-forget-password.html')
                
        except Exception as e:
            print(f"Error sending email: {e}")
            import traceback
            traceback.print_exc()
            flash("Error processing request. Please try again.", "error")
            return render_template('tenant-forget-password.html')
    
    @staticmethod
    @t_auth_bp.route('/verify_reset_code', methods=["POST"])
    def verify_reset_code():
        code = request.form.get("verification_code", '').strip()
        stored_code = session.get("verification_code")
        expiry = session.get('email_code_expiry')
        
        if not stored_code or not expiry:
            flash("Session expired. Please try again.", "error")
            return redirect(url_for("t_auth.forget_pass"))
        
        if datetime.now().timestamp() > expiry:
            session.pop('verification_code', None)
            session.pop('email_code_expiry', None)
            flash("Code expired. Please try again.", "error")
            return redirect(url_for("t_auth.forget_pass"))
        
        if code == stored_code:
            flash("Verification successful", "success")
            return render_template("tenant-forget.html")
        else:
            flash("Invalid verification code. Try again.", "error")
            return render_template("tenant-verify-code.html")
    
    @staticmethod
    @t_auth_bp.route('/reset_password', methods=['POST'])
    def reset_password():
        password = request.form.get('newpass', '').strip()
        confirm_password = request.form.get('confirmpass', '').strip()
        
        if not password or not confirm_password:
            flash("All fields are required", "error")
            return render_template("tenant-forget.html")
        
        if len(password) < 8:
            flash("Password should be at least 8 characters", "error")
            return render_template("tenant-forget.html")
        
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("tenant-forget.html")
        
        student_id = session.get("student_id")
        if not student_id:
            flash("Session expired. Please try again.", "error")
            return redirect(url_for("t_auth.forget_pass"))
        
        # Update password in tenant_auth collection
        try:
            if db.change_tenant_password(student_id, password):
                # Clear session data
                session.pop('verification_code', None)
                session.pop('email_code_expiry', None)
                session.pop('student_id', None)
                session.pop('student_email', None)
                
                flash("Password reset successfully! You can now login with your new password.", "success")
                return redirect(url_for('t_auth.signin_page'))
            else:
                flash("Error updating password. Please try again.", "error")
                return render_template("tenant-forget.html")
        except Exception as e:
            print(f"Error resetting password: {e}")
            flash("Error updating password. Please try again.", "error")
            return render_template("tenant-forget.html")
    
    @staticmethod
    @t_auth_bp.route('/validateSignup', methods=["POST"])
    def submit_reg():
        ten_id = request.form.get('TenantId')
        password = request.form.get('password')
        confirm_p = request.form.get('confirmPassword')
        
        if not ten_id or not password or not confirm_p:
            flash("All fields are required", "error")
            return redirect(url_for("t_auth.signup_page"))
        
        if not db.validate_tenant(ten_id):
            flash("Tenant ID does not exist", "error")
            return redirect(url_for("t_auth.signup_page"))
        
        if len(str(password)) < 8:
            flash("Password should be atleast 8 characters", "error")
            return redirect(url_for("t_auth.signup_page"))
            
        if password != confirm_p:
            flash("Passwords do not match", "error")
            return redirect(url_for("t_auth.signup_page"))
                        
        if db.signup_tenant(ten_id, password):
            flash("Account created successfully", "success")
            return redirect(url_for('t_auth.signin_page'))
        else:
            flash("Unknown error occured", "error")
            return redirect(url_for('t_auth.signup_page'))
    
    @staticmethod
    @t_auth_bp.route('/validateSignin', methods=['POST'])
    def validate_signin():
        ten_id = request.form.get('tenantId', '').strip()
        password = request.form.get('password', '').strip()
        
        if not ten_id or not password:
            flash("All fields are required", "error")
            return redirect(url_for("t_auth.signin_page"))
        
        # Check if tenant exists
        if not db.validate_tenant(ten_id):
            flash("Student ID does not exist. Please check your ID or register first.", "error")
            return redirect(url_for("t_auth.signin_page"))
        
        # Try to login
        try:
            if db.login_tenant(ten_id, password):
                session['tenant_id'] = ten_id
                session.permanent = True
                flash("Login successful! Welcome back.", "success")
                return redirect(url_for('t_dashboard.dashboard_page'))
            else:
                flash("Incorrect password. Please try again.", "error")
                return redirect(url_for('t_auth.signin_page'))
        except Exception as e:
            print(f"Login error: {e}")
            flash("An error occurred during login. Please try again.", "error")
            return redirect(url_for('t_auth.signin_page'))
    
    @staticmethod
    @t_auth_bp.route("/logout")
    def logout():
        session.clear()
        flash("Logged out successfully", "success")
        return redirect(url_for('starting_menu'))
        
    

        
        
        
        
    
    
            
    