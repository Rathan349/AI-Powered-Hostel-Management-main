from flask import request, render_template, flash, redirect, url_for, Blueprint, session
from admin.database.firebase import Database
from datetime import datetime, timedelta
from utils.email_service import EmailService
import random 

db = Database()
auth_bp = Blueprint('auth',
                    __name__,
                    template_folder="../templates",
                    static_folder="../static",
                    static_url_path="/admin_static"
                    )
  
class AuthRoutes:
        
    @staticmethod
    @auth_bp.route('/signup')
    def signup_page():
        return render_template('signup.html')
    
    @staticmethod
    @auth_bp.route("/submit", methods=["POST"])
    def submit():
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        c_password = request.form['cpassword']
        
        if not name or not email or not password or not c_password:
            flash("All fields are required", "error")
            return redirect(url_for("auth.signup_page"))
        
        if len(str(password)) < 8:
            flash("Password should be atleast 8 characters", "error")
            return redirect(url_for("auth.signup_page"))
            
        if password != c_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("auth.signup_page"))
        
        if db.user_exists(username=name):
            flash("Username already taken", "error")
            return redirect(url_for('auth.signup_page'))
        
        if db.user_exists(email=email):
            flash("Email already registered", "error")
            return redirect(url_for('auth.signup_page'))

        db.add_user(name, email, password)
        flash("Account created successfully", "success")
        return redirect(url_for('auth.signin_page'))
    
    @staticmethod
    @auth_bp.route('/signin')
    def signin_page():
        return render_template('signin.html')
    
    @staticmethod
    @auth_bp.route('/validate', methods=["POST"])
    def validate_login():
        name = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not name or not password:
            flash("All fields are required", "error")
            return redirect(url_for("auth.signin_page"))
        
        # Check if user exists
        if not db.user_exists(username=name):
            flash("Username does not exist. Please check your username or register first.", "error")
            return redirect(url_for("auth.signin_page"))
        
        # Try to login
        try:
            result = db.login_user(name, password)
            
            if result:
                # Set session
                session['username'] = name
                session.permanent = True
                flash("Login successful! Welcome back.", "success")
                return redirect(url_for('dashboard.mainpage'))
            else:
                flash("Incorrect password. Please try again.", "error")
                return redirect(url_for("auth.signin_page"))
        except Exception as e:
            print(f"Login error: {e}")
            flash("An error occurred during login. Please try again.", "error")
            return redirect(url_for("auth.signin_page"))
    
    @staticmethod
    @auth_bp.route('/signin/verify_user')
    def verify_user():
        return render_template('verify_user.html')
    
    @staticmethod
    @auth_bp.route('/signin/verify_code', methods=["POST"])
    def verify_code():
        try:
            username_or_email = request.form.get('username_or_email', '').strip()

            if not username_or_email:
                flash("Please enter username or email", "error")
                return render_template('verify_user.html')

            if db.validate_email(username_or_email):
                # It's an email
                if db.user_exists(email=username_or_email):
                    code = str(random.randint(100000, 999999))
                    session["verification_code"] = code
                    session['email_code_expiry'] = (datetime.now() + timedelta(minutes=5)).timestamp()
                    session["user_email"] = username_or_email
                    session["email"] = True

                    # Send email using EmailService
                    success, message = EmailService.send_verification_code(username_or_email, code, "Admin User")
                    
                    if success:
                        flash("Verification code sent to your email", "success")
                        return render_template("verify_code.html")
                    else:
                        flash(f"Error sending email: {message}", "error")
                        return render_template('verify_user.html')
                else:
                    flash("Email not found in our records", "error")
                    return render_template('verify_user.html')
            else:
                # It's a username
                if db.user_exists(username=username_or_email):
                    email = db.get_field("users", "username", username_or_email, "email")

                    if not email:
                        flash("No email found for this username", "error")
                        return render_template('verify_user.html')

                    code = str(random.randint(100000, 999999))
                    session["verification_code"] = code
                    session['email_code_expiry'] = (datetime.now() + timedelta(minutes=5)).timestamp()
                    session["user_email"] = username_or_email
                    session["email"] = False

                    # Send email using EmailService
                    success, message = EmailService.send_verification_code(email, code, username_or_email)
                    
                    if success:
                        flash("Verification code sent to your registered email", "success")
                        return render_template("verify_code.html")
                    else:
                        flash(f"Error sending email: {message}", "error")
                        return render_template('verify_user.html')
                else:
                    flash("Username not found in our records", "error")
                    return render_template('verify_user.html')
        except Exception as e:
            print(f"Error in verify_code: {e}")
            flash("Error processing request. Please try again.", "error")
            return render_template('verify_user.html')
        
    @staticmethod
    @auth_bp.route('/signin/verify_code/validate', methods=["POST"])
    def validate_verf_code():
        code = request.form.get("digit_code")
        stored_code = session.get("verification_code")
        expiry = session.get('email_code_expiry')

        
        if not stored_code or not expiry:
             flash("Session expired. Please try again.", "error")
             return redirect(url_for("auth.verify_user"))
        
        if datetime.now().timestamp() > expiry:
            session.pop('verification_code', None)
            session.pop('email_code_expiry', None)
            flash("Code expired. Please try again.", "error")
            return redirect(url_for("auth.verify_user"))
        
        if code == stored_code:
            flash("Verification Successful", "success")
            return render_template("new_password.html")
        
        else:
            flash("Invalid verification code. Try again.", "error")
            return render_template("verify_code.html")
            
    @staticmethod
    @auth_bp.route('/changepassword', methods=['POST'])
    def change_pass():
        password = request.form.get('newpass', '').strip()
        cpassword = request.form.get('confirmpass', '').strip()
        
        if not password or not cpassword:
            flash("All fields are required", "error")
            return render_template("new_password.html")
        
        if len(password) < 8:
            flash("Password should be at least 8 characters", "error")
            return render_template("new_password.html")
        
        if password != cpassword:
            flash("Passwords do not match", "error")
            return render_template("new_password.html")
        
        try:
            if session.get("email"):
                db.change_user_password(password, username=None, email=session.get("user_email"))
            else:
                db.change_user_password(password, username=session.get("user_email"), email=None)
            
            # Clear session data
            session.pop('verification_code', None)
            session.pop('email_code_expiry', None)
            session.pop('user_email', None)
            session.pop('email', None)
            
            flash("Password changed successfully", "success")
            return redirect(url_for('auth.signin_page'))
        except Exception as e:
            print(f"Error changing password: {e}")
            flash("Error changing password. Please try again.", "error")
            return render_template("new_password.html")
    
    @staticmethod
    @auth_bp.route('/logout')
    def logout():
        session.clear()
        flash("Logged out successfully", "success")
        return redirect(url_for('starting_menu'))
