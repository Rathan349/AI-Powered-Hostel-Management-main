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
                print("✅ Admin Database connected to Firebase Firestore")
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
            if not self.db:
                return False
                
            users_ref = self.db.collection('users')
            
            if username is not None:
                query = users_ref.where("username", "==", username.strip()).limit(1)
            elif email is not None:
                query = users_ref.where("email", "==", email.strip()).limit(1)
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
            if not self.db:
                return False
                
            users_ref = self.db.collection('users')
            query = users_ref.where("username", "==", name.strip()).where("password", "==", password.strip()).limit(1)
            docs = query.get()
            
            return len(docs) > 0
                
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
    
    def room_exists(self, room):
        try:
            rooms = self.db.collection('rooms').where('room_no', '==', room).get()
            return len(rooms) > 0
        except Exception as e:
            print(f"Error checking room exists: {e}")
            return False
    
    def count_rooms(self, d_board=False):
        try:
            if not d_board:
                room_ref = self.db.collection('rooms')
            else:
                room_ref = self.db.collection('rooms').where("status", "==", "Occupied")
            
            count_query = room_ref.count()
            result = count_query.get()
            count = result[0][0].value
            return int(count)
        except Exception as e:
            print(f"Error counting rooms: {e}")
            return 0
    
    def add_room(self, room_no, floor, capacity, ac, status):
        try:
            count = self.count_rooms()
            self.db.collection('rooms').document(f"room_{count + 1}").set({
                "room_no": room_no.strip(),
                "floor": floor.strip(),
                "capacity": int(capacity),
                "ac": ac,
                "status": status.strip()
            })
            
            print(f"Room_{count + 1} Added")
        except Exception as e:
            print(f"Error adding room: {e}")
    
    def get_rooms(self):
        try:
            room_refs = self.db.collection('rooms')
            rooms = room_refs.stream()
            
            available = [
                doc.to_dict().get('room_no')
                for doc in rooms
                if doc.to_dict().get('status') not in ["Occupied", "Under Maintenance"]
            ]
            
            return available
        except Exception as e:
            print(f"Error getting rooms: {e}")
            return []
    
    def get_tenants_details(self, ten_id=None, one_tenant=False):
        try:
            if not one_tenant:
                tenants_ref = self.db.collection('tenants')
                tenants = tenants_ref.stream()
                
                tenants_data = []
                for doc in tenants:
                    data = doc.to_dict()
                    info = (data.get('id'), 
                            data.get('name'),
                            data.get('room'),
                            data.get('type'),
                            data.get('date'),
                            data.get('status'))
                    tenants_data.append(info)
                
                return tenants_data
            else:
                tenant_data = self.get_tenant_s_details(ten_id)
                if tenant_data:
                    return (tenant_data.get('id'),
                            tenant_data.get('name'),
                            tenant_data.get('room'),
                            tenant_data.get('type'),
                            tenant_data.get('status'),
                            tenant_data.get('phone'),
                            tenant_data.get('email'),
                            tenant_data.get('date'),
                            tenant_data.get('ac'),
                            tenant_data.get('sleep_time'),
                            tenant_data.get('smoking'))
                return None
        except Exception as e:
            print(f"Error getting tenants details: {e}")
            return [] if not one_tenant else None
    
    def get_rooms_details(self, room_no=None, edit=False):
        try:
            if not edit:
                room_refs = self.db.collection('rooms')
                rooms = room_refs.stream()
                
                rooms_data = []
                
                for doc in rooms:
                    data = doc.to_dict()
                    info = (data.get('room_no'), 
                            data.get('floor'),
                            data.get('capacity'),
                            data.get('ac'),
                            data.get('status'))
                
                    rooms_data.append(info)
            else:
                rooms_data = self.db.collection('rooms').where('room_no', '==', room_no.strip()).get()[0].to_dict()
                rooms_data = (rooms_data.get('room_no'), 
                              rooms_data.get('floor'),
                              rooms_data.get('capacity'),
                              rooms_data.get('ac'),
                              rooms_data.get('status'))
                
            return rooms_data
        except Exception as e:
            print(f"Error getting rooms details: {e}")
            return [] if not edit else None
    
    def delete_document(self, collection, key, value):
        try:
            result = self.db.collection(collection).where(key.strip(), '==', value).get()
            self.db.collection(collection).document(result[0].id).delete()
            print(f"Document '{result[0].id}' deleted successfully from {collection}")
            return True
        except Exception as e:
            print("Error Deleting Document", e)
            return False
    
    def update_room_details(self, doc_id, room_no, floor, capacity, ac, status):
        try:
            self.db.collection('rooms').document(doc_id.strip()).set({
                "room_no": room_no.strip(),
                "floor": floor.strip(),
                "capacity": int(capacity),
                "ac": ac,
                "status": status.strip()
            })
            
            print(f"Room Data with {doc_id} is updated")
        except Exception as e:
            print(f"Error updating room: {e}")
    
    def save_mess_menu(self, week_menu):
        try:
            self.db.collection("mess").document("strange_menu").set(week_menu)
            print("Menu Saved Successfully")
        except Exception as e:
            print(f"Error saving menu: {e}")
    
    def get_mess_data(self):
        try:
            today_date = str(date.today())
            
            doc = self.db.collection("messAttendance").document(today_date).get()
            mess_data = doc.to_dict() or {} 
            
            new_list = []

            for ten_id, attendance in mess_data.items():
                try:
                    ten_name = self.get_tenant_s_details(ten_id, "name")
                except Exception as e:
                    ten_name = f"Unknown ({ten_id})"
                    print(f"Error fetching tenant name: {e}")

                new_list.append({
                    "name": ten_name,
                    "attendance": attendance
                })

            return new_list
        except Exception as e:
            print(f"Error getting mess data: {e}")
            return []
    
    def get_complaint_details(self):
        try:
            comp_details = self.db.collection("complaints").get()
            
            complaints = []
            
            for detail in comp_details:
                detail = detail.to_dict()
                complaints.append((detail.get("id"), 
                                   detail.get("ten_name"), 
                                   detail.get("ten_room"),
                                   detail.get("description"),
                                   detail.get("priority"),
                                   detail.get("status").capitalize()))
            
            return complaints
        except Exception as e:
            print(f"Error getting complaints: {e}")
            return []
    
    def update_complaint_status(self, comp_id):
        try:
            doc_id = self.get_doc_id("complaints", "id", comp_id)
            
            self.db.collection("complaints").document(doc_id).update({
                "status": "resolved"
            })
            
            print("Complaint Status Updated")
        except Exception as e:
            print(f"Error updating complaint status: {e}")
    
    def submit_complaint(self, tenant_id, description, complaint_type, priority):
        """Submit a new complaint"""
        try:
            # Get tenant details
            tenant = self.get_tenant_s_details(tenant_id)
            if not tenant:
                print(f"Tenant {tenant_id} not found")
                return False
            
            # Generate complaint ID
            complaints_ref = self.db.collection('complaints')
            try:
                count_query = complaints_ref.count()
                result = count_query.get()
                count = result[0][0].value
            except:
                count = 0
            
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

    # Message Methods
    def get_all_conversations(self):
        """Get all conversations grouped by student"""
        try:
            messages_ref = self.db.collection('messages')
            messages = messages_ref.stream()
            
            conversations = {}
            for doc in messages:
                data = doc.to_dict()
                sender_id = data.get('sender_id')
                receiver_id = data.get('receiver_id')
                sender_type = data.get('sender_type')
                
                # Group by student ID
                student_id = sender_id if sender_type == 'student' else receiver_id
                
                if student_id not in conversations:
                    conversations[student_id] = {
                        'student_id': student_id,
                        'last_message': data,
                        'unread_count': 0
                    }
                
                # Update if this is a newer message
                if data.get('timestamp', '') > conversations[student_id]['last_message'].get('timestamp', ''):
                    conversations[student_id]['last_message'] = data
                
                # Count unread messages to admin
                if data.get('receiver_type') == 'admin' and not data.get('read', False):
                    conversations[student_id]['unread_count'] += 1
            
            return list(conversations.values())
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
    
    def count_unread_messages(self, user_id, user_type):
        """Count unread messages for a user"""
        try:
            messages_ref = self.db.collection('messages')
            query = messages_ref.where('receiver_id', '==', user_id).where('receiver_type', '==', user_type).where('read', '==', False)
            docs = query.get()
            return len(docs)
        except Exception as e:
            print(f"Error counting unread messages: {e}")
            return 0
    
    def get_messages(self, user_id, user_type, inbox=True):
        """Get messages for a user (inbox or sent)"""
        try:
            messages_ref = self.db.collection('messages')
            
            if inbox:
                query = messages_ref.where('receiver_id', '==', user_id).where('receiver_type', '==', user_type)
            else:
                query = messages_ref.where('sender_id', '==', user_id).where('sender_type', '==', user_type)
            
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
    
    def broadcast_message(self, sender_id, subject, message):
        """Send message to all students"""
        try:
            tenants = self.get_tenants_details()
            count = 0
            
            for tenant in tenants:
                tenant_id = tenant[0]
                self.send_message(sender_id, 'admin', tenant_id, 'student', subject, message)
                count += 1
            
            return count
        except Exception as e:
            print(f"Error broadcasting message: {e}")
            return 0
    
    def send_message(self, sender_id, sender_type, receiver_id, receiver_type, subject, message):
        """Send a message"""
        try:
            timestamp = datetime.now().isoformat()
            
            self.db.collection('messages').add({
                'sender_id': sender_id,
                'sender_type': sender_type,
                'receiver_id': receiver_id,
                'receiver_type': receiver_type,
                'subject': subject,
                'message': message,
                'timestamp': timestamp,
                'read': False
            })
            
            print(f"Message sent from {sender_id} to {receiver_id}")
        except Exception as e:
            print(f"Error sending message: {e}")
    
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
    
    def get_conversation(self, admin_id, student_id):
        """Get conversation between admin and student"""
        try:
            messages_ref = self.db.collection('messages')
            
            # Get messages where admin is sender and student is receiver
            query1 = messages_ref.where('sender_id', '==', admin_id).where('receiver_id', '==', student_id)
            docs1 = query1.stream()
            
            # Get messages where student is sender and admin is receiver
            query2 = messages_ref.where('sender_id', '==', student_id).where('receiver_id', '==', admin_id)
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
            print(f"Error getting conversation: {e}")
            return []
    
    def delete_conversation(self, admin_id, student_id):
        """Delete entire conversation between admin and student"""
        try:
            messages = self.get_conversation(admin_id, student_id)
            
            for message in messages:
                self.delete_message(message['id'])
            
            return True
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return False
    
    # Fee Methods
    def get_all_fees(self):
        """Get all fee records"""
        try:
            fees_ref = self.db.collection('fees')
            docs = fees_ref.stream()
            
            fees = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                
                # Get student name
                try:
                    student_data = self.get_tenant_s_details(data.get('student_id'))
                    data['student_name'] = student_data.get('name', 'Unknown') if student_data else 'Unknown'
                except:
                    data['student_name'] = 'Unknown'
                
                fees.append(data)
            
            return fees
        except Exception as e:
            print(f"Error getting fees: {e}")
            return []
    
    def add_fee_record(self, student_id, amount, due_date, fee_type):
        """Add a new fee record"""
        try:
            self.db.collection('fees').add({
                'student_id': int(student_id),
                'amount': float(amount),
                'due_date': due_date,
                'fee_type': fee_type,
                'status': 'pending',
                'paid_amount': 0,
                'created_at': datetime.now().isoformat()
            })
            
            print(f"Fee record added for student {student_id}")
        except Exception as e:
            print(f"Error adding fee record: {e}")
    
    def update_fee_payment(self, fee_id, paid_amount, paid_date, payment_method, transaction_id=None, notes=None):
        """Update fee payment information"""
        try:
            update_data = {
                'paid_amount': float(paid_amount),
                'paid_date': paid_date,
                'payment_method': payment_method,
                'status': 'paid',
                'updated_at': datetime.now().isoformat()
            }
            
            if transaction_id:
                update_data['transaction_id'] = transaction_id
            if notes:
                update_data['notes'] = notes
            
            self.db.collection('fees').document(fee_id).update(update_data)
            
            print(f"Fee payment updated for {fee_id}")
        except Exception as e:
            print(f"Error updating fee payment: {e}")
    
    def get_fee_by_id(self, fee_id):
        """Get a specific fee record by ID"""
        try:
            doc = self.db.collection('fees').document(fee_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                
                # Get student name
                try:
                    student_data = self.get_tenant_s_details(data.get('student_id'))
                    data['student_name'] = student_data.get('name', 'Unknown') if student_data else 'Unknown'
                except:
                    data['student_name'] = 'Unknown'
                
                return data
            return None
        except Exception as e:
            print(f"Error getting fee by ID: {e}")
            return None
    
    def export_fees_to_excel(self):
        """Export fees to Excel"""
        try:
            fees = self.get_all_fees()
            df = pd.DataFrame(fees)
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Fees', index=False)
            output.seek(0)
            return output
        except Exception as e:
            print(f"Error exporting fees: {e}")
            return BytesIO()
    
    def get_payment_history(self, fee_id=None, student_id=None):
        """Get payment history"""
        try:
            if fee_id:
                # Get specific fee record
                fee_data = self.get_fee_by_id(fee_id)
                return [fee_data] if fee_data else []
            elif student_id:
                # Get all fees for a student
                fees_ref = self.db.collection('fees')
                query = fees_ref.where('student_id', '==', int(student_id))
                docs = query.stream()
                
                payments = []
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    payments.append(data)
                
                return payments
            else:
                return []
        except Exception as e:
            print(f"Error getting payment history: {e}")
            return []

    # Leave Request Management Methods
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
    
    def get_pending_leave_requests(self):
        """Get all pending leave requests for admin approval"""
        try:
            requests_ref = self.db.collection("leave_requests")
            docs = requests_ref.stream()
            
            requests = []
            for doc in docs:
                request_data = doc.to_dict()
                if request_data.get('status') == 'Pending':
                    requests.append(request_data)
            
            # Sort by submitted_at in Python
            requests.sort(key=lambda x: x.get('submitted_at', ''), reverse=True)
            return requests
        except Exception as e:
            print(f"Error getting pending leave requests: {e}")
            return []
    
    def get_all_leave_requests(self):
        """Get all leave requests with status"""
        try:
            requests_ref = self.db.collection("leave_requests")
            docs = requests_ref.stream()
            
            requests = []
            for doc in docs:
                request_data = doc.to_dict()
                requests.append(request_data)
            
            # Sort by submitted_at in Python
            requests.sort(key=lambda x: x.get('submitted_at', ''), reverse=True)
            return requests
        except Exception as e:
            print(f"Error getting leave requests: {e}")
            return []
    
    def approve_leave_request(self, request_id, admin_id):
        """Approve a leave request and generate QR code"""
        try:
            # Get the request
            doc_ref = self.db.collection("leave_requests").document(request_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False, "Request not found"
            
            request_data = doc.to_dict()
            
            # Generate pass ID and update status
            pass_id = f"L{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            updates = {
                'status': 'Approved',
                'approved_at': datetime.now().isoformat(),
                'approved_by': admin_id,
                'pass_id': pass_id
            }
            
            doc_ref.update(updates)
            
            print(f"Leave request {request_id} approved successfully")
            return True, pass_id
        except Exception as e:
            print(f"Error approving leave request: {e}")
            return False, str(e)
    
    def reject_leave_request(self, request_id, admin_id, reason=None):
        """Reject a leave request"""
        try:
            doc_ref = self.db.collection("leave_requests").document(request_id)
            
            updates = {
                'status': 'Rejected',
                'rejected_at': datetime.now().isoformat(),
                'rejected_by': admin_id,
                'rejection_reason': reason or 'No reason provided'
            }
            
            doc_ref.update(updates)
            
            print(f"Leave request {request_id} rejected successfully")
            return True
        except Exception as e:
            print(f"Error rejecting leave request: {e}")
            return False
    
    # Visitor Request Management Methods
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
    
    def get_pending_visitor_requests(self):
        """Get all pending visitor requests for admin approval"""
        try:
            requests_ref = self.db.collection("visitor_requests")
            docs = requests_ref.stream()
            
            requests = []
            for doc in docs:
                request_data = doc.to_dict()
                if request_data.get('status') == 'Pending':
                    requests.append(request_data)
            
            # Sort by submitted_at in Python
            requests.sort(key=lambda x: x.get('submitted_at', ''), reverse=True)
            return requests
        except Exception as e:
            print(f"Error getting pending visitor requests: {e}")
            return []
    
    def get_all_visitor_requests(self):
        """Get all visitor requests with status"""
        try:
            requests_ref = self.db.collection("visitor_requests")
            docs = requests_ref.stream()
            
            requests = []
            for doc in docs:
                request_data = doc.to_dict()
                requests.append(request_data)
            
            # Sort by submitted_at in Python
            requests.sort(key=lambda x: x.get('submitted_at', ''), reverse=True)
            return requests
        except Exception as e:
            print(f"Error getting visitor requests: {e}")
            return []
    
    def approve_visitor_request(self, request_id, admin_id):
        """Approve a visitor request and generate QR code"""
        try:
            # Get the request
            doc_ref = self.db.collection("visitor_requests").document(request_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False, "Request not found"
            
            request_data = doc.to_dict()
            
            # Generate visitor ID and update status
            visitor_id = f"V{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            updates = {
                'status': 'Approved',
                'approved_at': datetime.now().isoformat(),
                'approved_by': admin_id,
                'visitor_id': visitor_id
            }
            
            doc_ref.update(updates)
            
            print(f"Visitor request {request_id} approved successfully")
            return True, visitor_id
        except Exception as e:
            print(f"Error approving visitor request: {e}")
            return False, str(e)
    
    def reject_visitor_request(self, request_id, admin_id, reason=None):
        """Reject a visitor request"""
        try:
            doc_ref = self.db.collection("visitor_requests").document(request_id)
            
            updates = {
                'status': 'Rejected',
                'rejected_at': datetime.now().isoformat(),
                'rejected_by': admin_id,
                'rejection_reason': reason or 'No reason provided'
            }
            
            doc_ref.update(updates)
            
            print(f"Visitor request {request_id} rejected successfully")
            return True
        except Exception as e:
            print(f"Error rejecting visitor request: {e}")
            return False
    
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

if __name__ == "__main__":
    app = Database()
    print("Firebase Database initialized successfully")