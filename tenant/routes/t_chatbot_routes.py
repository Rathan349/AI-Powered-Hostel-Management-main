from flask import request, render_template, flash, redirect, url_for, Blueprint, session, jsonify
from tenant.database.firebase import Database
from utils.chatbot_utils import chatbot

db = Database()
t_chatbot_bp = Blueprint('t_chatbot',
                         __name__,
                         template_folder="../templates")

class TChatbotRoutes:
    
    @staticmethod
    @t_chatbot_bp.route('/chatbot')
    def chatbot_page():
        """Display chatbot interface"""
        student_id = session.get('tenant_id')
        if not student_id:
            flash("Please login first", "error")
            return redirect(url_for('t_auth.signin_page'))
        
        return render_template('student_chatbot.html')
    
    @staticmethod
    @t_chatbot_bp.route('/chat', methods=['POST'])
    def chat():
        """Handle chat messages"""
        student_id = session.get('tenant_id')
        if not student_id:
            return jsonify({
                'success': False,
                'message': 'Please login first'
            })
        
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'message': 'Message cannot be empty'
            })
        
        # Get enhanced AI bot response
        bot_response = chatbot.get_response(user_message, student_id)
        
        # Add contextual info for specific queries
        if any(word in user_message.lower() for word in ['my', 'me', 'i', 'profile', 'dashboard']):
            contextual_info = chatbot.get_contextual_info(student_id, db)
            if contextual_info:
                bot_response = contextual_info + "\n\n" + bot_response
        
        # Get proactive suggestions
        suggestions = chatbot.get_proactive_suggestions(student_id, db)
        if suggestions and len(user_message.split()) < 3:  # Short queries get suggestions
            bot_response += "\n\n🔔 **Proactive Alerts:**\n" + "\n".join(f"• {s}" for s in suggestions)
        
        return jsonify({
            'success': True,
            'response': bot_response,
            'timestamp': str(datetime.now().strftime('%H:%M'))
        })
    
    @staticmethod
    @t_chatbot_bp.route('/quick_actions', methods=['POST'])
    def quick_actions():
        """Handle quick action buttons"""
        student_id = session.get('tenant_id')
        if not student_id:
            return jsonify({
                'success': False,
                'message': 'Please login first'
            })
        
        data = request.json
        action = data.get('action')
        
        responses = {
            'mess_timing': chatbot.knowledge_base['mess']['responses']['timing'],
            'fee_status': "Check your fee status in the 'My Fees' section of your dashboard.",
            'submit_complaint': "To submit a complaint, go to 'Submit Complaint' in your dashboard and fill out the form.",
            'room_info': chatbot.get_contextual_info(student_id, db),
            'contact_admin': "You can message the admin through the Messages section or email: admin@hostel.com"
        }
        
        response = responses.get(action, "I can help you with that! Please ask me a specific question.")
        
        return jsonify({
            'success': True,
            'response': response
        })

from datetime import datetime
