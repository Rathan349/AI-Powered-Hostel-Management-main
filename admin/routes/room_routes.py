from flask import request, render_template, flash, redirect, url_for, Blueprint
from admin.database.firebase import Database

room_bp = Blueprint('room',
                    __name__,
                    template_folder="../templates",
                    static_folder="static",
                    static_url_path="/admin_static")
db = Database()

class RoomRoutes:
    
    @staticmethod
    @room_bp.route('/addroom')
    def add_room():
        return render_template('add_room.html')
    
    @staticmethod
    @room_bp.route('/addroom/adding', methods=['POST'])
    def adding_room():
        room_no = request.form.get('roomNumber')
        floor = request.form.get('floor')
        capacity = request.form.get('capacity')
        ac = request.form.get('ac')
        status = request.form.get('status')
        
        if not room_no or not floor or not capacity or not ac or not status:
            flash("All fields are required", "error")
            return render_template("add_room.html")
        
        if db.room_exists(room_no):
            flash("Room already exists", "error")
            return render_template('add_room.html')
        
        if status == "--Select Status--":
            flash("Please select valid status")
            return render_template('add_room.html')
        
        db.add_room(room_no, floor, capacity, ac, status)
        
        flash("Room added successfully", "success")
        return render_template('add_room.html')
    
    @staticmethod
    @room_bp.route('/delete/<room_id>', methods=['POST'])
    def delete_room(room_id):
        
        db.delete_document("rooms", "room_no", room_id)
        return redirect(url_for('dashboard.manage_rooms'))
    
    @staticmethod
    @room_bp.route('/edit/<room_no>', methods=['GET'])
    def edit_room(room_no):
        room_data = db.get_rooms_details(room_no, True)
        room_id = db.get_doc_id("rooms", "room_no", room_no)
        
        return render_template(
            "add_room.html",
            mode="edit",
            room_no=room_no,
            room_data=room_data,
            room_id=room_id
        )
    
    @staticmethod
    @room_bp.route('edit/<doc_id>/update', methods=['POST'])
    def update_room(doc_id):
        room_no = request.form['roomNumber']
        floor = request.form['floor']
        capacity = request.form['capacity']
        ac = request.form['ac']
        status = request.form['status']
        
        db.update_room_details(doc_id, room_no, floor, capacity, ac, status)
        
        return redirect(url_for('dashboard.manage_rooms'))
        
        
        
        
        


            
            
        
        