from flask import Flask
from flask_socketio import SocketIO
from connection.connection import init_db, db
from routes.auth_routes import auth_bp
from routes.chat_routes import chat_bp, init_socketio
from routes.app_routes import app_bp, init_socketio as init_app_socketio
from models.message import Message
from routes.ai_routes import ai_bp

app = Flask(__name__)
init_db(app)
socketio = SocketIO(app, manage_session=False)
init_socketio(socketio)
init_app_socketio(socketio)

app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(app_bp)
app.register_blueprint(ai_bp, url_prefix='/ai')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, port=5337)