import warnings
import re
from datetime import date, datetime
import pandas as pd
from io import BytesIO
from firebase_connection import firebase_connection
from firebase_admin import firestore

warnings.filterwarnings("ignore")

class Database:
    _db_instance = None
    
    def __init__(self):
        if Database._db_instance is None:
            self.connect()
            Database._db_instance = self.db
        else:
            self.db = Database._db_instance
    
    def connect(self):
        """Connect to Firebase Firestore using singleton connection"""
        try:
            self.db = firebase_connection.get_db()
            if self.db:
                print("✅ Tenant Database connected to Firebase Firestore")
            else:
                print("❌ Failed to connect to Firebase Firestore")
        except Exception as e:
            print(f"❌ Error connecting to Firebase: {e}")
            self.db = None
    
    # Attendance Methods
    def mark_attendance(self, student_id, date_str, status):
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            timestamp = datetime.now().isoformat()
            
            doc_ref = self.db.collection("attendance").document(f"{student_id}_{date_str}")
            doc_ref.set({
                "tenant_id": student_id,
                "student_id": student_id,
                "date": date_str,
                "status": status,
                "time": current_time,
                "timestamp": timestamp
            })
            
            print(f"Attendance marked for student {student_id}")
        except Exception as e:
            print(f"Error marking attendance: {e}")
    
    def get_attendance_by_date(self, date_str):
        try:
            attendance_ref = self.db.collection("attendance")
            query = attendance_ref.where("date", "==", date_str)
            docs = query.stream()
            
            result = []
            for doc in docs:
                data = doc.to_dict()
                result.append(data)
            
            return result
        except Exception as e:
            print(f"Error getting attendance: {e}")
            return []
    
    def get_all_attendance(self, start_date=None, end_date=None):
        try:
            attendance_ref = self.db.collection("attendance")
            
            if start_date and end_date:
                query = attendance_ref.where("date", ">=", start_date).where("date", "<=", end_date)
            else:
                query = attendance_ref
            
            docs = query.stream()
            
            result = []
            for doc in docs:
                data = doc.to_dict()
                # Get student name from tenants collection
                try:
                    tenant_doc = self.db.collection("tenants").where("id", "==", data.get("tenant_id")).get()
                    if tenant_doc:
                        tenant_data = tenant_doc[0].to_dict()
                        data["student_name"] = tenant_data.get("name", "Unknown")
                        data["room_number"] = tenant_data.get("room", "N/A")
                except:
                    data["student_name"] = "Unknown"
                    data["room_number"] = "N/A"
                
                result.append(data)
            
            return result
        except Exception as e:
            print(f"Error getting all attendance: {e}")
            return []
    
    def export_attendance_to_excel(self):
        attendance = self.get_all_attendance()
        df = pd.DataFrame(attendance)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Attendance', index=False)
        output.seek(0)
        return output
    
    def get_doc_id(self, col_name, key, value):
        try:
            collection_ref = self.db.collection(col_name)
            query = collection_ref.where(key, "==", value)
            docs = query.get()
            
            if docs:
                return docs[0].id
            return None
        except Exception as e:
            print(f"Error getting document ID: {e}")
            return None
        
    def count_users(self):
        try:
            users_ref = self.db.collection('users')
            count_query = users_ref.count()
            result = count_query.get()
            count = result[0][0].value
            return int(count)
        except Exception as e:
            print(f"Error counting users: {e}")
            return 0
    
    def validate_email(self, input_str):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, input_str) is not None
            
    def user_exists(self, username=None, email=None):
        try:
            users_ref = self.db.collection('users')
            
            if username is not None:
                query = users_ref.where("username", "==", username.strip())
            elif email is not None:
                query = users_ref.where("email", "==", email.strip())
            else:
                return False
            
            docs = query.get()
            return len(docs) > 0
        except Exception as e:
            print(f"Error checking user exists: {e}")
            return False
    
    def get_field(self, collection, key, value, required):
        try:
            field = self.db.collection(collection).where(key, "==", value).get()[0]
            return field.to_dict().get(required)
        except Exception as e:
            print(f"Error getting field: {e}")
            return None
    
    def change_user_password(self, password, username=None, email=None):
        try:
            if username is not None:
                doc_id = self.get_doc_id("users", "username", username.strip())
                if doc_id:
                    self.db.collection("users").document(doc_id).update({
                        "password": password
                    })

            if email is not None:
                doc_id = self.get_doc_id("users", "email", email.strip())
                if doc_id:
                    self.db.collection("users").document(doc_id).update({
                        "password": password
                    })

            print("Password Changed Successfully")
        except Exception as e:
            print(f"Error changing password: {e}")

    def add_user(self, name, email, password):
        try:
            count = self.count_users()
            self.db.collection('users').document(f"user_{count + 1}").set({
                "username": f"{name.strip()}",
                "email": f"{email.strip()}",
                "password": f"{password.strip()}"
            })
            
            print(f"User_{count + 1} Added")
        except Exception as e:
            print(f"Error adding user: {e}")

    def login_user(self, name, password):
        try:
            users_ref = self.db.collection('users')
            query = users_ref.where("username", "==", name.strip()).where("password", "==", password.strip())
            docs = query.get()
            
            if docs:
                print(f"Login successful for user {name}")
                return True
            else:
                print(f"Invalid credentials for user {name}")
                return False
                
        except Exception as e:
            print(f"Error in login_user: {e}")
            return False
    
    def count_tenants(self):
        try:
            tenants_ref = self.db.collection('tenants')
            count_query = tenants_ref.count()
            result = count_query.get()
            count = result[0][0].value
            return int(count)
        except Exception as e:
            print(f"Error counting tenants: {e}")
            return 0
    
    def count_complaints(self):
        try:
            com_ref = self.db.collection('complaints').where("status", "==", "pending")
            count_query = com_ref.count()
            result = count_query.get()
            count = result[0][0].value
            return int(count)
        except Exception as e:
            print(f"Error counting complaints: {e}")
            return 0
    
    def count_mess(self):
        try:
            today_date = str(date.today())
            
            doc_ref = self.db.collection("messAttendance").document(today_date)
            doc = doc_ref.get()

            if doc.exists:
                attendance_data = doc.to_dict()
                count = len(attendance_data)  
                return count
            else:
                return 0
        except Exception as e:
            print(f"Error counting mess: {e}")
            return 0
    
    def update_tenant(self, id, name, t_type, email, phone, date, ac, sleep, smoking, room, status):
        try:
            doc_id = self.get_doc_id("tenants", "id", int(id))
            self.db.collection('tenants').document(doc_id).set({
                "id": int(id),
                "name": f"{name.strip()}",
                "type": f"{t_type.strip()}",
                "email": f"{email.strip()}",
                "phone": f"{phone.strip()}",
                "room": f"{room.strip()}",
                "date": f"{date.strip()}",
                "ac": f"{ac.strip()}",
                "sleep_time": f"{sleep.strip()}",
                "smoking": f"{smoking.strip()}",
                "status": f"{status}"
            }, merge=True)
            
            print("Tenant details updated successfully")
        except Exception as e:
            print(f"Error updating tenant: {e}")
    
    def add_tenant(self, id, name, t_type, email, phone, date, ac, sleep, smoking, room, status):
        try:
            count = self.count_tenants()
            self.db.collection('tenants').document(f"ten_{count + 1}").set({
                "id": int(id),
                "name": f"{name.strip()}",
                "type": f"{t_type.strip()}",
                "email": f"{email.strip()}",
                "phone": f"{phone.strip()}",
                "room": f"{room.strip()}",
                "date": f"{date.strip()}",
                "ac": f"{ac.strip()}",
                "sleep_time": f"{sleep.strip()}",
                "smoking": f"{smoking.strip()}",
                "status": f"{status}"
            })
            
            print(f"Tenant_{count + 1} Added")
        except Exception as e:
            print(f"Error adding tenant: {e}")
    
    def get_tenant_s_details(self, ten_id, key=None):
        try:
            ten_doc = self.get_doc_id("tenants", "id", int(ten_id))
            doc_ref = self.db.collection("tenants").document(ten_doc).get()
            
            if doc_ref.exists:
                doc = doc_ref.to_dict()
                
                if key is not None:
                    return doc.get(key.strip())
                else:
                    return doc
            return None
        except Exception as e:
            print(f"Error getting tenant details: {e}")
            return None
    
    # Tenant-specific methods
    def validate_tenant(self, tenant_id):
        """Check if tenant ID exists"""
        try:
            if not self.db:
                return False
                
            tenants_ref = self.db.collection('tenants')
            query = tenants_ref.where("id", "==", int(tenant_id)).limit(1)
            docs = query.get()
            return len(docs) > 0
        except Exception as e:
            print(f"Error validating tenant: {e}")
            return False
    
    def signup_tenant(self, tenant_id, password):
        """Create tenant login credentials"""
        try:
            # Check if tenant already has login credentials
            auth_ref = self.db.collection('tenant_auth')
            query = auth_ref.where("tenant_id", "==", tenant_id)
            docs = query.get()
            
            if docs:
                return False  # Already exists
            
            # Create new tenant auth
            self.db.collection('tenant_auth').document(f"auth_{tenant_id}").set({
                "tenant_id": tenant_id,
                "password": password
            })
            
            print(f"Tenant {tenant_id} signup successful")
            return True
        except Exception as e:
            print(f"Error signing up tenant: {e}")
            return False
    
    def login_tenant(self, tenant_id, password):
        """Authenticate tenant login"""
        try:
            if not self.db:
                return False
                
            auth_ref = self.db.collection('tenant_auth')
            query = auth_ref.where("tenant_id", "==", tenant_id).where("password", "==", password).limit(1)
            docs = query.get()
            
            return len(docs) > 0
        except Exception as e:
            print(f"Error logging in tenant: {e}")
            return False
    
    def get_tenant_details(self, tenant_id, field=None):
        """Get tenant details (alias for get_tenant_s_details)"""
        return self.get_tenant_s_details(tenant_id, field)
    
    def get_room_details(self, tenant_id):
        """Get room details for a tenant"""
        try:
            tenant = self.get_tenant_s_details(tenant_id)
            if tenant and tenant.get('room'):
                room_no = tenant.get('room')
                rooms_ref = self.db.collection('rooms')
                query = rooms_ref.where("room_no", "==", room_no)
                docs = query.get()
                
                if docs:
                    return docs[0].to_dict()
            return None
        except Exception as e:
            print(f"Error getting room details: {e}")
            return None
    
    def get_room_tenant_details(self, tenant_id, room_no):
        """Get all tenants in the same room"""
        try:
            tenants_ref = self.db.collection('tenants')
            query = tenants_ref.where("room", "==", room_no).where("status", "==", "active")
            docs = query.stream()
            
            result = []
            for doc in docs:
                data = doc.to_dict()
                result.append(data)
            
            return result
        except Exception as e:
            print(f"Error getting room tenant details: {e}")
            return []
    
    def get_menu_data(self):
        """Get mess menu data"""
        try:
            menu_doc = self.db.collection("mess").document("strange_menu").get()
            if menu_doc.exists:
                return menu_doc.to_dict()
            return {}
        except Exception as e:
            print(f"Error getting menu data: {e}")
            return {}
    
    def get_complaint_details(self, tenant_id):
        """Get complaints for a specific tenant"""
        try:
            complaints_ref = self.db.collection('complaints')
            query = complaints_ref.where("ten_id", "==", str(tenant_id))
            docs = query.stream()
            
            result = []
            for doc in docs:
                data = doc.to_dict()
                result.append(data)
            
            return result
        except Exception as e:
            print(f"Error getting complaint details: {e}")
            return []
    
    def submit_complaint(self, tenant_id, description, complaint_type, priority):
        """Submit a new complaint"""
        try:
            # Get tenant details
            tenant = self.get_tenant_s_details(tenant_id)
            if not tenant:
                return False
            
            # Generate complaint ID
            complaints_ref = self.db.collection('complaints')
            count_query = complaints_ref.count()
            result = count_query.get()
            count = result[0][0].value
            
            complaint_id = f"COMP_{int(count) + 1:04d}"
            
            self.db.collection('complaints').document(complaint_id).set({
                "id": complaint_id,
                "ten_id": str(tenant_id),
                "ten_name": tenant.get('name'),
                "ten_room": tenant.get('room'),
                "description": description,
                "complaint_type": complaint_type,
                "priority": priority,
                "status": "pending",
                "created_at": datetime.now().isoformat()
            })
            
            print(f"Complaint {complaint_id} submitted successfully")
            return True
        except Exception as e:
            print(f"Error submitting complaint: {e}")
            return False
    
    def save_tenant_attendance(self, tenant_id, breakfast, lunch, dinner):
        """Save tenant mess attendance"""
        try:
            today = str(date.today())
            
            attendance_data = {}
            if breakfast:
                attendance_data["breakfast"] = True
            if lunch:
                attendance_data["lunch"] = True
            if dinner:
                attendance_data["dinner"] = True
            
            # Update the mess attendance document
            doc_ref = self.db.collection("messAttendance").document(today)
            doc_ref.set({
                str(tenant_id): attendance_data
            }, merge=True)
            
            print(f"Mess attendance saved for tenant {tenant_id}")
            return True
        except Exception as e:
            print(f"Error saving mess attendance: {e}")
            return False

    # Message Methods for Tenants
    def get_my_messages(self, student_id, inbox=True):
        """Get messages for a student (inbox or sent)"""
        try:
            messages_ref = self.db.collection('messages')
            
            if inbox:
                query = messages_ref.where('receiver_id', '==', int(student_id)).where('receiver_type', '==', 'student')
            else:
                query = messages_ref.where('sender_id', '==', int(student_id)).where('sender_type', '==', 'student')
            
            docs = query.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
            
            messages = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                messages.append(data)
            
            return messages
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
    
    def count_unread_messages(self, student_id):
        """Count unread messages for a student"""
        try:
            messages_ref = self.db.collection('messages')
            query = messages_ref.where('receiver_id', '==', int(student_id)).where('receiver_type', '==', 'student').where('read', '==', False)
            docs = query.get()
            return len(docs)
        except Exception as e:
            print(f"Error counting unread messages: {e}")
            return 0
    
    def send_message_to_admin(self, student_id, subject, message):
        """Send a message to admin"""
        try:
            timestamp = datetime.now().isoformat()
            
            self.db.collection('messages').add({
                'sender_id': int(student_id),
                'sender_type': 'student',
                'receiver_id': 'admin',
                'receiver_type': 'admin',
                'subject': subject,
                'message': message,
                'timestamp': timestamp,
                'read': False
            })
            
            print(f"Message sent from student {student_id} to admin")
        except Exception as e:
            print(f"Error sending message to admin: {e}")
    
    def get_message_by_id(self, message_id):
        """Get a specific message by ID"""
        try:
            doc = self.db.collection('messages').document(message_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            print(f"Error getting message: {e}")
            return None
    
    def mark_message_read(self, message_id):
        """Mark a message as read"""
        try:
            self.db.collection('messages').document(message_id).update({'read': True})
            print(f"Message {message_id} marked as read")
        except Exception as e:
            print(f"Error marking message as read: {e}")
    
    def delete_message(self, message_id):
        """Delete a message"""
        try:
            self.db.collection('messages').document(message_id).delete()
            print(f"Message {message_id} deleted")
            return True
        except Exception as e:
            print(f"Error deleting message: {e}")
            return False
    
    def get_conversation_with_admin(self, student_id):
        """Get conversation between student and admin"""
        try:
            messages_ref = self.db.collection('messages')
            
            # Get messages where student is sender and admin is receiver
            query1 = messages_ref.where('sender_id', '==', int(student_id)).where('receiver_type', '==', 'admin')
            docs1 = query1.stream()
            
            # Get messages where admin is sender and student is receiver
            query2 = messages_ref.where('receiver_id', '==', int(student_id)).where('sender_type', '==', 'admin')
            docs2 = query2.stream()
            
            messages = []
            for doc in docs1:
                data = doc.to_dict()
                data['id'] = doc.id
                messages.append(data)
            
            for doc in docs2:
                data = doc.to_dict()
                data['id'] = doc.id
                messages.append(data)
            
            # Sort by timestamp
            messages.sort(key=lambda x: x.get('timestamp', ''))
            
            return messages
        except Exception as e:
            print(f"Error getting conversation with admin: {e}")
            return []
    
    def delete_conversation_with_admin(self, student_id):
        """Delete entire conversation between student and admin"""
        try:
            messages = self.get_conversation_with_admin(student_id)
            
            for message in messages:
                self.delete_message(message['id'])
            
            return True
        except Exception as e:
            print(f"Error deleting conversation with admin: {e}")
            return False

    # Leave Request Methods for Students
    def submit_leave_request(self, student_id, student_name, room, leave_from, leave_to, purpose, destination, emergency_contact):
        """Submit a leave request for admin approval"""
        try:
            request_id = f"LR{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            leave_request = {
                'request_id': request_id,
                'student_id': student_id,
                'student_name': student_name,
                'room': room,
                'leave_from': leave_from,
                'leave_to': leave_to,
                'purpose': purpose,
                'destination': destination,
                'emergency_contact': emergency_contact,
                'status': 'Pending',
                'submitted_at': datetime.now().isoformat(),
                'approved_at': None,
                'approved_by': None,
                'qr_code': None,
                'pass_id': None
            }
            
            doc_ref = self.db.collection("leave_requests").document(request_id)
            doc_ref.set(leave_request)
            
            print(f"Leave request {request_id} submitted successfully")
            return request_id
        except Exception as e:
            print(f"Error submitting leave request: {e}")
            return None
    
    def get_my_leave_requests(self, student_id):
        """Get all leave requests for a specific student"""
        try:
            requests_ref = self.db.collection("leave_requests")
            docs = requests_ref.stream()
            
            requests = []
            for doc in docs:
                request_data = doc.to_dict()
                if str(request_data.get('student_id')) == str(student_id):
                    requests.append(request_data)
            
            # Sort by submitted_at in Python
            requests.sort(key=lambda x: x.get('submitted_at', ''), reverse=True)
            return requests
        except Exception as e:
            print(f"Error getting student leave requests: {e}")
            return []
    
    def get_leave_request_by_id(self, request_id):
        """Get a specific leave request by ID"""
        try:
            doc_ref = self.db.collection("leave_requests").document(request_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting leave request: {e}")
            return None
    
    # Visitor Request Methods for Students
    def submit_visitor_request(self, student_id, student_name, room, visitor_name, visitor_phone, visit_date, entry_time, purpose, valid_until):
        """Submit a visitor request for admin approval"""
        try:
            request_id = f"VR{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            visitor_request = {
                'request_id': request_id,
                'student_id': student_id,
                'student_name': student_name,
                'room': room,
                'visitor_name': visitor_name,
                'visitor_phone': visitor_phone,
                'visit_date': visit_date,
                'entry_time': entry_time,
                'purpose': purpose,
                'valid_until': valid_until,
                'status': 'Pending',
                'submitted_at': datetime.now().isoformat(),
                'approved_at': None,
                'approved_by': None,
                'qr_code': None,
                'visitor_id': None
            }
            
            doc_ref = self.db.collection("visitor_requests").document(request_id)
            doc_ref.set(visitor_request)
            
            print(f"Visitor request {request_id} submitted successfully")
            return request_id
        except Exception as e:
            print(f"Error submitting visitor request: {e}")
            return None
    
    def get_my_visitor_requests(self, student_id):
        """Get all visitor requests for a specific student"""
        try:
            requests_ref = self.db.collection("visitor_requests")
            docs = requests_ref.stream()
            
            requests = []
            for doc in docs:
                request_data = doc.to_dict()
                if str(request_data.get('student_id')) == str(student_id):
                    requests.append(request_data)
            
            # Sort by submitted_at in Python
            requests.sort(key=lambda x: x.get('submitted_at', ''), reverse=True)
            return requests
        except Exception as e:
            print(f"Error getting student visitor requests: {e}")
            return []
    
    def get_visitor_request_by_id(self, request_id):
        """Get a specific visitor request by ID"""
        try:
            doc_ref = self.db.collection("visitor_requests").document(request_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting visitor request: {e}")
            return None

    def get_tenant_by_email(self, email):
        """Get tenant details by email"""
        try:
            tenants_ref = self.db.collection('tenants')
            query = tenants_ref.where("email", "==", email.strip())
            docs = query.get()
            
            if docs:
                return docs[0].to_dict()
            return None
        except Exception as e:
            print(f"Error getting tenant by email: {e}")
            return None
    
    def tenant_has_auth(self, tenant_id):
        """Check if tenant has authentication credentials"""
        try:
            auth_ref = self.db.collection('tenant_auth')
            query = auth_ref.where("tenant_id", "==", str(tenant_id))
            docs = query.get()
            return len(docs) > 0
        except Exception as e:
            print(f"Error checking tenant auth: {e}")
            return False
    
    def change_tenant_password(self, tenant_id, new_password):
        """Change tenant password"""
        try:
            doc_id = self.get_doc_id("tenant_auth", "tenant_id", str(tenant_id))
            if doc_id:
                self.db.collection("tenant_auth").document(doc_id).update({
                    "password": new_password
                })
                print(f"Password changed for tenant {tenant_id}")
                return True
            return False
        except Exception as e:
            print(f"Error changing tenant password: {e}")
            return False

if __name__ == "__main__":
    app = Database()
    print("Tenant Firebase Database initialized successfully")