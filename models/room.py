
from connection.connection import db

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(8), unique=True, nullable=False)
    is_public = db.Column(db.Boolean, default=False)