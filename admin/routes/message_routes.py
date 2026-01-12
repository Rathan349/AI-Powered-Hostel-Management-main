from flask import request, render_template, flash, redirect, url_for, Blueprint, session, jsonify
from admin.database.firebase import Database
from datetime import datetime, date, timedelta

db = Database()
message_bp = Blueprint('message',
                      __name__,
                      template_folder="../templates")

class MessageRoutes:
    
    @staticmethod
    @message_bp.route('/inbox')
    def inbox():
        """View inbox messages - shows list of conversations"""
        admin_id = session.get('username', 'admin')
        
        # Get all conversations grouped by student
        conversations = db.get_all_conversations()
        total_unread = db.count_unread_messages(admin_id, 'admin')
        
        return render_template('messages_list.html', 
                             conversations=conversations, 
                             total_unread=total_unread)
    
    @staticmethod
    @message_bp.route('/sent')
    def sent():
        """View sent messages"""
        admin_id = session.get('username', 'admin')
        messages = db.get_messages(admin_id, 'admin', inbox=False)
        
        return render_template('messages_sent.html', 
                             messages=messages,
                             active_tab='sent')
    
    @staticmethod
    @message_bp.route('/compose', methods=['GET', 'POST'])
    def compose():
        """Compose a new message"""
        if request.method == 'POST':
            receiver_id = request.form.get('receiver_id')
            subject = request.form.get('subject')
            message = request.form.get('message')
            
            if not receiver_id or not subject or not message:
                flash("All fields are required", "error")
                return redirect(url_for('message.compose'))
            
            admin_id = session.get('username', 'admin')
            
            # Check if it's a broadcast
            if receiver_id == 'all':
                count = db.broadcast_message(admin_id, subject, message)
                flash(f"Message broadcast to {count} students successfully", "success")
            else:
                db.send_message(admin_id, 'admin', receiver_id, 'student', subject, message)
                flash("Message sent successfully", "success")
            
            return redirect(url_for('message.sent'))
        
        # Get all students for dropdown
        students = db.get_tenants_details()
        
        return render_template('compose_message.html', students=students)
    
    @staticmethod
    @message_bp.route('/view/<message_id>')
    def view_message(message_id):
        """View a specific message"""
        message = db.get_message_by_id(message_id)
        
        if not message:
            flash("Message not found", "error")
            return redirect(url_for('message.inbox'))
        
        # Mark as read if it's in inbox
        admin_id = session.get('username', 'admin')
        if message.get('receiver_id') == admin_id and not message.get('read'):
            db.mark_message_read(message_id)
        
        return render_template('view_message.html', message=message)
    
    @staticmethod
    @message_bp.route('/reply/<message_id>', methods=['GET', 'POST'])
    def reply(message_id):
        """Reply to a message"""
        original_message = db.get_message_by_id(message_id)
        
        if not original_message:
            flash("Original message not found", "error")
            return redirect(url_for('message.inbox'))
        
        if request.method == 'POST':
            reply_text = request.form.get('message')
            
            if not reply_text:
                flash("Message cannot be empty", "error")
                return redirect(url_for('message.reply', message_id=message_id))
            
            admin_id = session.get('username', 'admin')
            sender_id = original_message.get('sender_id')
            subject = f"Re: {original_message.get('subject')}"
            
            db.send_message(admin_id, 'admin', sender_id, 'student', subject, reply_text)
            flash("Reply sent successfully", "success")
            return redirect(url_for('message.inbox'))
        
        return render_template('reply_message.html', original_message=original_message)
    
    @staticmethod
    @message_bp.route('/delete/<message_id>', methods=['POST'])
    def delete(message_id):
        """Delete a message"""
        if db.delete_message(message_id):
            flash("Message deleted successfully", "success")
        else:
            flash("Failed to delete message", "error")
        
        return redirect(url_for('message.inbox'))
    
    @staticmethod
    @message_bp.route('/conversation/<student_id>', methods=['GET', 'POST'])
    def conversation(student_id):
        """View conversation thread with a student"""
        admin_id = session.get('username', 'admin')
        
        if request.method == 'POST':
            reply_text = request.form.get('message')
            
            if reply_text:
                # Get the last message to use its subject
                messages = db.get_conversation(admin_id, student_id)
                if messages:
                    last_subject = messages[-1].get('subject', 'Chat')
                    subject = f"Re: {last_subject}" if not last_subject.startswith('Re:') else last_subject
                else:
                    subject = "Chat Message"
                
                db.send_message(admin_id, 'admin', int(student_id), 'student', subject, reply_text)
                flash("Message sent successfully", "success")
                return redirect(url_for('message.conversation', student_id=student_id))
        
        # Get all messages between admin and this student
        messages = db.get_conversation(admin_id, student_id)
        
        return render_template('conversation.html', messages=messages, student_id=student_id)
    
    @staticmethod
    @message_bp.route('/delete_conversation/<student_id>', methods=['POST'])
    def delete_conversation(student_id):
        """Delete entire conversation with a student"""
        admin_id = session.get('username', 'admin')
        
        if db.delete_conversation(admin_id, student_id):
            flash("Conversation deleted successfully", "success")
        else:
            flash("Failed to delete conversation", "error")
        
        return redirect(url_for('message.inbox'))
    
    # WhatsApp-style Chat Routes
    @staticmethod
    @message_bp.route('/whatsapp_chat')
    def whatsapp_chat():
        """WhatsApp-style chat interface"""
        if 'username' not in session:
            return redirect(url_for('auth.signin_page'))
        
        return render_template('whatsapp_chat.html')
    
    @staticmethod
    @message_bp.route('/api/conversations')
    def api_conversations():
        """API endpoint to get all conversations"""
        if 'username' not in session:
            return {'error': 'Unauthorized'}, 401
        
        try:
            conversations = db.get_all_conversations()
            
            # Format conversations for API
            formatted_conversations = []
            for conv in conversations:
                # Get student name
                try:
                    student_data = db.get_tenant_s_details(conv['student_id'])
                    student_name = student_data.get('name', f'Student {conv["student_id"]}') if student_data else f'Student {conv["student_id"]}'
                except:
                    student_name = f'Student {conv["student_id"]}'
                
                # Format timestamp
                last_msg = conv.get('last_message', {})
                timestamp = last_msg.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        if dt.date() == date.today():
                            time_str = dt.strftime('%I:%M %p')
                        elif dt.date() == date.today() - timedelta(days=1):
                            time_str = 'Yesterday'
                        else:
                            time_str = dt.strftime('%m/%d/%y')
                    except:
                        time_str = 'Recently'
                else:
                    time_str = 'Recently'
                
                formatted_conversations.append({
                    'student_id': str(conv['student_id']),
                    'student_name': student_name,
                    'last_message': last_msg.get('message', 'No messages yet')[:50] + ('...' if len(last_msg.get('message', '')) > 50 else ''),
                    'timestamp': time_str,
                    'unread_count': conv.get('unread_count', 0)
                })
            
            return {'conversations': formatted_conversations}
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return {'conversations': []}
    
    @staticmethod
    @message_bp.route('/api/conversation/<student_id>')
    def api_conversation(student_id):
        """API endpoint to get conversation with specific student"""
        if 'username' not in session:
            return {'error': 'Unauthorized'}, 401
        
        try:
            admin_id = session.get('username', 'admin')
            messages = db.get_conversation(admin_id, student_id)
            
            # Format messages for API
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    'id': msg.get('id'),
                    'sender_type': msg.get('sender_type'),
                    'message': msg.get('message'),
                    'timestamp': msg.get('timestamp'),
                    'date': msg.get('timestamp', '')[:10] if msg.get('timestamp') else ''
                })
            
            return {'messages': formatted_messages}
        except Exception as e:
            print(f"Error getting conversation: {e}")
            return {'messages': []}
    
    @staticmethod
    @message_bp.route('/api/send', methods=['POST'])
    def api_send_message():
        """API endpoint to send message"""
        if 'username' not in session:
            return {'error': 'Unauthorized'}, 401
        
        try:
            data = request.get_json()
            student_id = data.get('student_id')
            message = data.get('message')
            
            if not student_id or not message:
                return {'success': False, 'error': 'Missing required fields'}
            
            admin_id = session.get('username', 'admin')
            subject = 'Chat Message'
            
            db.send_message(admin_id, 'admin', int(student_id), 'student', subject, message)
            
            return {'success': True}
        except Exception as e:
            print(f"Error sending message: {e}")
            return {'success': False, 'error': str(e)}
