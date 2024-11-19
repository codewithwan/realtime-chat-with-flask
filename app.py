from flask import Flask
from connection.connection import db, init_db
from routes.auth_routes import auth_bp
from routes.app_routes import app_bp, init_socketio
from flask_socketio import SocketIO

app = Flask(__name__)
init_db(app)

app.register_blueprint(auth_bp)
app.register_blueprint(app_bp)

socketio = SocketIO(app, manage_session=False)
init_socketio(socketio)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, port=5001)