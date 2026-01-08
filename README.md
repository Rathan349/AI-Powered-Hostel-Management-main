# 🏨 AI-Powered Hostel Management System

A comprehensive Flask-based hostel management system with Firebase Firestore integration, featuring AI-powered analytics, QR code integration, and automated workflows.

## ✨ Features

### 🔐 **Authentication & Security**
- **Admin Panel**: Secure admin dashboard with role-based access
- **Student Portal**: Self-service portal for students/tenants
- **Forgot Password**: Email-based password reset system
- **Session Management**: Secure session handling with expiry

### 🏠 **Core Management Features**
- **Room Management**: Track room availability, assignments, and capacity
- **Student Management**: Complete tenant registration and profile management
- **Fee Management**: Handle payments, fee tracking, and payment history
- **Attendance Tracking**: Monitor student attendance with smart analytics
- **Complaint System**: Manage and resolve student complaints with priority classification

### 💬 **Communication System**
- **Internal Messaging**: Secure communication between admin and students
- **Broadcast Messages**: Send announcements to all students
- **Real-time Notifications**: Instant updates and alerts
- **Conversation Management**: Organized message threads

### 🤖 **AI-Powered Features**
- **Smart Analytics**: AI-driven insights and predictions
- **Priority Classification**: Automatic complaint priority assignment
- **Chatbot Integration**: AI assistant for common queries
- **Predictive Analytics**: Forecast occupancy and trends

### 📱 **Digital Integration**
- **QR Code System**: Digital ID cards and access control
- **Mobile-Friendly**: Responsive design for all devices
- **Digital Documents**: Paperless document management
- **Visitor Management**: QR-based visitor tracking

### 🍽️ **Mess Management**
- **Menu Planning**: Weekly menu management
- **Attendance Tracking**: Meal attendance monitoring
- **Food Analytics**: Consumption patterns and waste reduction

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Firebase account with Firestore enabled
- Gmail account for email services (or other SMTP provider)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/AI-Powered-Hostel-Management.git
   cd AI-Powered-Hostel-Management
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Firebase Setup**
   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
   - Enable Firestore Database
   - Generate service account key:
     - Go to Project Settings → Service Accounts
     - Click "Generate new private key"
     - Save the JSON file as `serviceAccountKey.json` in the project root

5. **Email Configuration**
   - Update email settings in `app.py`:
   ```python
   app.config['MAIL_USERNAME'] = "your-email@gmail.com"
   app.config['MAIL_PASSWORD'] = "your-app-password"  # Use App Password for Gmail
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open your browser and go to: `http://localhost:5000`

## 📖 Usage Guide

### 🔑 **First Time Setup**

1. **Admin Account Creation**
   - Go to `/admin/signup`
   - Create your admin account
   - Login at `/admin_login`

2. **Add Students/Tenants**
   - Navigate to "Manage Tenants" in admin panel
   - Add student details including email addresses
   - Students can then register at `/tenant/signup`

### 🎯 **Key Workflows**

#### **For Administrators:**
1. **Dashboard**: Overview of occupancy, complaints, and analytics
2. **Room Management**: Add/edit rooms, assign students
3. **Fee Management**: Track payments, generate reports
4. **Complaint Resolution**: View and resolve student issues
5. **Messaging**: Communicate with students, send broadcasts

#### **For Students:**
1. **Profile Management**: Update personal information
2. **Fee Tracking**: View payment history and pending dues
3. **Complaint Submission**: Report issues with priority levels
4. **Messaging**: Communicate with admin
5. **QR Access**: Use digital ID for various services

## 🏗️ Project Structure

```
AI-Powered-Hostel-Management/
├── admin/                          # Admin panel modules
│   ├── database/                   # Admin database operations
│   │   └── firebase.py            # Admin Firebase operations
│   ├── routes/                     # Admin route handlers
│   │   ├── auth_routes.py         # Authentication routes
│   │   ├── dashboard_routes.py    # Dashboard functionality
│   │   ├── tenant_routes.py       # Student management
│   │   ├── room_routes.py         # Room management
│   │   ├── fee_routes.py          # Fee management
│   │   ├── complaint_routes.py    # Complaint handling
│   │   ├── message_routes.py      # Messaging system
│   │   └── ai_routes.py           # AI features
│   ├── static/                     # Admin static files
│   │   └── styles.css             # Admin styling
│   └── templates/                  # Admin HTML templates
├── tenant/                         # Student portal modules
│   ├── database/                   # Student database operations
│   ├── routes/                     # Student route handlers
│   ├── static/                     # Student static files
│   └── templates/                  # Student HTML templates
├── utils/                          # Utility modules
│   ├── email_service.py           # Email functionality
│   ├── chatbot_utils.py           # AI chatbot utilities
│   ├── ml_utils.py                # Machine learning utilities
│   └── qr_utils.py                # QR code generation
├── static/                         # Global static files
├── templates/                      # Main application templates
├── app.py                          # Main Flask application
├── firebase_connection.py          # Firebase configuration
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🔧 Configuration

### **Environment Variables**
Create a `.env` file (optional) for sensitive configurations:
```env
FLASK_SECRET_KEY=your-secret-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
FIREBASE_PROJECT_ID=your-project-id
```

### **Firebase Collections Structure**
The system uses the following Firestore collections:
- `users` - Admin user accounts
- `tenants` - Student/tenant information
- `tenant_auth` - Student login credentials
- `rooms` - Room information and availability
- `complaints` - Student complaints and issues
- `messages` - Internal messaging system
- `fees` - Fee records and payment tracking
- `attendance` - Attendance records
- `messAttendance` - Meal attendance tracking

## 🛠️ API Endpoints

### **Admin Routes**
- `GET /admin_login` - Admin login page
- `POST /admin/validate` - Admin authentication
- `GET /AdminDashboard/` - Admin dashboard
- `GET /manage_tenants/` - Student management
- `GET /manage_rooms/` - Room management
- `GET /manage_fees/` - Fee management

### **Student Routes**
- `GET /tenant_login` - Student login page
- `POST /tenant/validateSignin` - Student authentication
- `GET /TenantDashboard/` - Student dashboard
- `GET /Complaint/` - Complaint submission
- `GET /student_messages/` - Student messaging

### **API Features**
- RESTful design principles
- JSON response format
- Error handling and validation
- Session-based authentication

## 🤖 AI Features

### **Machine Learning Models**
- **Complaint Priority Classifier**: Automatically categorizes complaints by urgency
- **Occupancy Prediction**: Forecasts room occupancy trends
- **Fee Payment Prediction**: Identifies students at risk of payment delays

### **Chatbot Integration**
- Natural language processing for student queries
- Automated responses for common questions
- Escalation to human support when needed

### **Analytics Dashboard**
- Real-time occupancy statistics
- Payment trend analysis
- Complaint resolution metrics
- Student satisfaction insights

## 📧 Email System

The system includes a robust email service for:
- Password reset verification codes
- Payment reminders and notifications
- Complaint status updates
- System announcements

**Email Features:**
- HTML and plain text support
- Template-based messaging
- Automatic retry mechanism
- Delivery status tracking

## 🔒 Security Features

- **Password Hashing**: Secure password storage
- **Session Management**: Automatic session expiry
- **Input Validation**: SQL injection prevention
- **CSRF Protection**: Cross-site request forgery prevention
- **Role-based Access**: Admin and student role separation
- **Email Verification**: Account verification system

## 📱 Mobile Responsiveness

The system is fully responsive and works seamlessly on:
- Desktop computers
- Tablets
- Mobile phones
- Various screen sizes and orientations

## 🧪 Testing

### **Manual Testing**
1. **Admin Functions**: Test all admin panel features
2. **Student Functions**: Verify student portal functionality
3. **Email System**: Test forgot password and notifications
4. **QR Codes**: Verify QR code generation and scanning

### **Performance Testing**
- Database query optimization
- Page load speed testing
- Concurrent user handling
- Memory usage monitoring

## 🚀 Deployment

### **Local Development**
```bash
python app.py
```

### **Production Deployment**
1. **Use a production WSGI server** (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

2. **Set up reverse proxy** (Nginx recommended)

3. **Configure SSL/HTTPS** for security

4. **Set up monitoring** and logging

### **Cloud Deployment Options**
- **Heroku**: Easy deployment with buildpacks
- **Google Cloud Platform**: Native Firebase integration
- **AWS**: Elastic Beanstalk or EC2
- **DigitalOcean**: App Platform or Droplets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### **Development Guidelines**
- Follow PEP 8 style guidelines
- Add comments for complex logic
- Write descriptive commit messages
- Test thoroughly before submitting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### **Common Issues**

1. **Firebase Connection Error**
   - Ensure `serviceAccountKey.json` is in the project root
   - Verify Firebase project settings
   - Check internet connectivity

2. **Email Not Working**
   - Verify Gmail app password setup
   - Check SMTP settings in `app.py`
   - Ensure "Less secure app access" is enabled (if not using app passwords)

3. **Login Issues**
   - Clear browser cache and cookies
   - Check database connection
   - Verify user credentials in Firestore

### **Getting Help**
- 📧 Email: support@hostelmanager.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/AI-Powered-Hostel-Management/issues)
- 📖 Documentation: [Wiki](https://github.com/your-username/AI-Powered-Hostel-Management/wiki)

## 🙏 Acknowledgments

- **Flask Framework**: Web application framework
- **Firebase**: Backend-as-a-Service platform
- **Bootstrap**: Frontend CSS framework
- **Scikit-learn**: Machine learning library
- **QR Code Libraries**: QR code generation and processing

## 📊 Project Stats

- **Languages**: Python, HTML, CSS, JavaScript
- **Framework**: Flask
- **Database**: Firebase Firestore
- **Features**: 50+ implemented features
- **Templates**: 30+ responsive HTML templates
- **Routes**: 40+ API endpoints

---

**Made with ❤️ for efficient hostel management**

*Last updated: December 2024*
