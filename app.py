from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import check_password_hash
import bcrypt
from functools import wraps
from flask_socketio import SocketIO, join_room, leave_room, send
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 's3cr3t'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
socketio = SocketIO(app, manage_session=False)

online_users = set()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(8), unique=True, nullable=False)
    is_public = db.Column(db.Boolean, default=False)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(username=username, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except:
            db.session.rollback()
            flash('Username already exists. Please choose a different username.', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    online_users_count = len(online_users)
    rooms = Room.query.filter_by(is_public=True).all()
    for room in rooms:
        room.user_count = len(socketio.server.manager.rooms.get('/', {}).get(room.room_code, []))
    return render_template('dashboard.html', username=session.get('username'), online_users=online_users_count, rooms=rooms)

@app.route('/create_room', methods=['POST'])
@login_required
def create_room():
    room_code = str(uuid.uuid4())[:8]
    is_public = request.form.get('is_public') == 'on'
    new_room = Room(room_code=room_code, is_public=is_public)
    db.session.add(new_room)
    db.session.commit()
    return redirect(url_for('chat', room_code=room_code))

@app.route('/join_room', methods=['POST'])
@login_required
def join_room_route():
    room_code = request.form['room_code']
    return redirect(url_for('chat', room_code=room_code))

# Remove the public_rooms route
# @app.route('/public_rooms')
# @login_required
# def public_rooms():
#     rooms = Room.query.filter_by(is_public=True).all()
#     for room in rooms:
#         room.user_count = len(socketio.server.manager.rooms.get('/', {}).get(room.room_code, []))
#     return render_template('public_rooms.html', rooms=rooms)

@app.route('/chat/<room_code>')
@login_required
def chat(room_code):
    room = Room.query.filter_by(room_code=room_code).first_or_404()
    return render_template('chat.html', username=session.get('username'), room_code=room_code, online_users=len(online_users))

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, port=5001)