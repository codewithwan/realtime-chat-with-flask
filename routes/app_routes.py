from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from connection.connection import db
from models.room import Room
from models.user import User
from flask_socketio import join_room, leave_room, send
from routes.auth_routes import login_required
import uuid

app_bp = Blueprint('app', __name__)
socketio = None

def init_socketio(sio):
    global socketio
    socketio = sio

    @socketio.on('connect')
    def handle_connect():
        online_users.add(request.sid)
        socketio.emit('update_online_users', {'online_users': len(online_users)})

    @socketio.on('disconnect')
    def handle_disconnect():
        online_users.discard(request.sid)
        socketio.emit('update_online_users', {'online_users': len(online_users)})
        # Remove empty public rooms
        for room in Room.query.filter_by(is_public=True).all():
            if len(socketio.server.manager.rooms.get('/', {}).get(room.room_code, [])) == 0:
                db.session.delete(room)
                db.session.commit()

    @socketio.on('join')
    def on_join(data):
        room = data['room']
        join_room(room)
        username = session.get("username")
        if username:
            send({'msg': f'{username} has entered the room.'}, to=room)

    @socketio.on('leave')
    def on_leave(data):
        room = data['room']
        leave_room(room)
        username = session.get("username")
        if username:
            send({'msg': f'{username} has left the room.'}, to=room)
        # Check if the room is empty and delete if it's a public room
        if len(socketio.server.manager.rooms.get('/', {}).get(room, [])) == 0:
            room_record = Room.query.filter_by(room_code=room).first()
            if room_record and room_record.is_public:
                db.session.delete(room_record)
                db.session.commit()

    @socketio.on('message')
    def handle_message(data):
        room = data['room']
        username = session.get('username')
        if username:
            send({'msg': data['msg'], 'username': username}, to=room)

online_users = set()

@app_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('app.dashboard'))
    return redirect(url_for('auth.login'))

@app_bp.route('/dashboard')
@login_required
def dashboard():
    online_users_count = len(online_users)
    rooms = Room.query.filter_by(is_public=True).all()
    for room in rooms:
        room.user_count = len(socketio.server.manager.rooms.get('/', {}).get(room.room_code, []))
    return render_template('dashboard.html', username=session.get('username'), online_users=online_users_count, rooms=rooms, ai_enabled=True)

@app_bp.route('/create_room', methods=['POST'])
@login_required
def create_room():
    room_code = str(uuid.uuid4())[:8]
    is_public = request.form.get('is_public') == 'on'
    new_room = Room(room_code=room_code, is_public=is_public)
    db.session.add(new_room)
    db.session.commit()
    return redirect(url_for('app.chat', room_code=room_code))

@app_bp.route('/join_room', methods=['POST'])
@login_required
def join_room_route():
    room_code = request.form['room_code']
    return redirect(url_for('app.chat', room_code=room_code))

@app_bp.route('/invite_user', methods=['POST'])
@login_required
def invite_user():
    invite_username = request.form['invite_username']
    user = User.query.filter_by(username=invite_username).first()
    if user:
        room_code = str(uuid.uuid4())[:8]
        new_room = Room(room_code=room_code, is_public=False)
        db.session.add(new_room)
        db.session.commit()
        return redirect(url_for('app.chat', room_code=room_code))
    flash('User not found', 'danger')
    return redirect(url_for('app.dashboard'))

@app_bp.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('app.dashboard'))

@app_bp.route('/chat/<room_code>')
@login_required
def chat(room_code):
    room = Room.query.filter_by(room_code=room_code).first()
    if not room:
        return redirect(url_for('app.dashboard'))
    return render_template('chat.html', username=session.get('username'), room_code=room_code, online_users=len(online_users))