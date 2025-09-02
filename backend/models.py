from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(30))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Team(db.Model):
    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(200), nullable=False)
    leader_name = db.Column(db.String(120))
    leader_email = db.Column(db.String(255))
    members = db.Column(db.Text)  # JSON or comma-separated list
    category = db.Column(db.String(80))
    status = db.Column(db.String(20), default="pending")  # pending/approved/rejected
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

class Seat(db.Model):
    __tablename__ = "seats"
    id = db.Column(db.Integer, primary_key=True)
    seat_code = db.Column(db.String(10), unique=True, nullable=False)
    row = db.Column(db.String(5))
    number = db.Column(db.Integer)
    status = db.Column(db.String(20), default="available")  # available/booked/blocked
    booked_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    booked_at = db.Column(db.DateTime, nullable=True)

class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey("seats.id"), nullable=False)
    booked_at = db.Column(db.DateTime, default=datetime.utcnow)
