from flask import request, render_template, flash, redirect, url_for, Blueprint, session, jsonify
from tenant.database.firebase import Database
from datetime import datetime, date, timedelta

db = Database()
t_message_bp = Blueprint('t_message',
                        __name__,
                        template_folder="../templates")

class TMessageRoutes:
    
    @staticmethod
    @t_message_bp.route('/inbox')
    def inbox():
        """View inbox messages"""
        student_id = session.get('tenant_id')
        if not student_id:
            flash("Please login first", "error")
            return redirect(url_for('t_auth.signin_page'))
        
        messages = db.get_my_messages(student_id, inbox=True)
        unread_count = db.count_unread_messages(student_id)
        
        return render_template('student_inbox.html', 
                             messages=messages, 
                             unread_count=unread_count,
                             active_tab='inbox')
    
    @staticmethod
    @t_message_bp.route('/sent')
    def sent():
        """View sent messages"""
        student_id = session.get('tenant_id')
        if not student_id:
            flash("Please login first", "error")
            return redirect(url_for('t_auth.signin_page'))
        
        messages = db.get_my_messages(student_id, inbox=False)
        
        return render_template('student_sent.html', 
                             messages=messages,
                             active_tab='sent')
    
    @staticmethod
    @t_message_bp.route('/compose', methods=['GET', 'POST'])
    def compose():
        """Compose a new message to admin"""
        student_id = session.get('tenant_id')
        if not student_id:
            flash("Please login first", "error")
            return redirect(url_for('t_auth.signin_page'))
        
        if request.method == 'POST':
            subject = request.form.get('subject')
            message = request.form.get('message')
            
            if not subject or not message:
                flash("All fields are required", "error")
                return redirect(url_for('t_message.compose'))
            
            db.send_message_to_admin(student_id, subject, message)
            flash("Message sent to admin successfully", "success")
            return redirect(url_for('t_message.sent'))
        
        return render_template('student_compose.html')
    
    @staticmethod
    @t_message_bp.route('/view/<message_id>')
    def view_message(message_id):
        """View a specific message"""
        student_id = session.get('tenant_id')
        if not student_id:
            flash("Please login first", "error")
            return redirect(url_for('t_auth.signin_page'))
        
        message = db.get_message_by_id(message_id)
        
        if not message:
            flash("Message not found", "error")
            return redirect(url_for('t_message.inbox'))
        
        # Mark as read if it's in inbox
        if str(message.get('receiver_id')) == str(student_id) and not message.get('read'):
            db.mark_message_read(message_id)
        
        return render_template('student_view_message.html', message=message)
    
    @staticmethod
    @t_message_bp.route('/reply/<message_id>', methods=['GET', 'POST'])
    def reply(message_id):
        """Reply to a message"""
        student_id = session.get('tenant_id')
        if not student_id:
            flash("Please login first", "error")
            return redirect(url_for('t_auth.signin_page'))
        
        original_message = db.get_message_by_id(message_id)
        
        if not original_message:
            flash("Original message not found", "error")
            return redirect(url_for('t_message.inbox'))
        
        if request.method == 'POST':
            reply_text = request.form.get('message')
            
            if not reply_text:
                flash("Message cannot be empty", "error")
                return redirect(url_for('t_message.reply', message_id=message_id))
            
            subject = f"Re: {original_message.get('subject')}"
            
            db.send_message_to_admin(student_id, subject, reply_text)
            flash("Reply sent successfully", "success")
            return redirect(url_for('t_message.inbox'))
        
        return render_template('student_reply.html', original_message=original_message)
    
    @staticmethod
    @t_message_bp.route('/delete/<message_id>', methods=['POST'])
    def delete(message_id):
        """Delete a message"""
        student_id = session.get('tenant_id')
        if not student_id:
            flash("Please login first", "error")
            return redirect(url_for('t_auth.signin_page'))
        
        # Get the message to check if student owns it
        message = db.get_message_by_id(message_id)
        if message:
            # Check if student is sender or receiver
            try:
                student_id_int = int(student_id)
            except:
                student_id_int = student_id
            
            if message.get('sender_id') == student_id_int or message.get('receiver_id') == student_id_int:
                if db.delete_message(message_id):
                    flash("Message deleted successfully", "success")
                else:
                    flash("Failed to delete message", "error")
            else:
                flash("You don't have permission to delete this message", "error")
        else:
            flash("Message not found", "error")
        
        return redirect(url_for('t_message.inbox'))
    
    @staticmethod
    @t_message_bp.route('/conversation', methods=['GET', 'POST'])
    def conversation():
        """View conversation thread with admin"""
        student_id = session.get('tenant_id')
        if not student_id:
            flash("Please login first", "error")
            return redirect(url_for('t_auth.signin_page'))
        
        if request.method == 'POST':
            reply_text = request.form.get('message')
            
            if reply_text:
                # Get the last message to use its subject
                messages = db.get_conversation_with_admin(student_id)
                if messages:
                    last_subject = messages[-1].get('subject', 'Chat')
                    subject = f"Re: {last_subject}" if not last_subject.startswith('Re:') else last_subject
                else:
                    subject = "Chat Message"
                
                db.send_message_to_admin(student_id, subject, reply_text)
                flash("Message sent successfully", "success")
                return redirect(url_for('t_message.conversation'))
        
        # Get all messages between student and admin
        messages = db.get_conversation_with_admin(student_id)
        
        return render_template('student_conversation.html', messages=messages)
    
    @staticmethod
    @t_message_bp.route('/delete_conversation', methods=['POST'])
    def delete_conversation():
        """Delete entire conversation with admin"""
        student_id = session.get('tenant_id')
        if not student_id:
            flash("Please login first", "error")
            return redirect(url_for('t_auth.signin_page'))
        
        if db.delete_conversation_with_admin(student_id):
            flash("Conversation deleted successfully", "success")
        else:
            flash("Failed to delete conversation", "error")
        
        return redirect(url_for('t_message.inbox'))
    
    # WhatsApp-style Chat Routes
    @staticmethod
    @t_message_bp.route('/whatsapp_chat')
    def whatsapp_chat():
        """WhatsApp-style chat interface for students"""
        student_id = session.get('tenant_id')
        if not student_id:
            flash("Please login first", "error")
            return redirect(url_for('t_auth.signin_page'))
        
        return render_template('student_whatsapp_chat.html')
    
    @staticmethod
    @t_message_bp.route('/api/conversation')
    def api_conversation():
        """API endpoint to get conversation with admin"""
        student_id = session.get('tenant_id')
        if not student_id:
            return {'error': 'Unauthorized'}, 401
        
        try:
            messages = db.get_conversation_with_admin(student_id)
            
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
    @t_message_bp.route('/api/send', methods=['POST'])
    def api_send_message():
        """API endpoint to send message to admin"""
        student_id = session.get('tenant_id')
        if not student_id:
            return {'error': 'Unauthorized'}, 401
        
        try:
            data = request.get_json()
            message = data.get('message')
            subject = data.get('subject', 'Chat Message')
            
            if not message:
                return {'success': False, 'error': 'Message is required'}
            
            db.send_message_to_admin(student_id, subject, message)
            
            return {'success': True}
        except Exception as e:
            print(f"Error sending message: {e}")
            return {'success': False, 'error': str(e)}
