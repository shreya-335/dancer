from flask import Flask, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY
from models import db, User, Team, Seat, Booking
from datetime import datetime
import os

app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

CORS(app)  # safe for localhost demo

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

# --- Frontend pages ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/seats")
def seats_page():
    return render_template("seats.html")

@app.route("/team-register")
def team_register_page():
    return render_template("team_register.html")

@app.route("/admin")
def admin_page():
    return render_template("admin.html")

# New separated auth pages
@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")


# --- API: auth & users ---
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone", "")
    if not email or not password:
        return jsonify({"status":"error", "message":"Email and password required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"status":"error", "message":"Email already registered"}), 400
    pw_hash = generate_password_hash(password)
    user = User(name=name, email=email, password_hash=pw_hash, phone=phone)
    db.session.add(user)
    db.session.commit()
    return jsonify({"status":"success", "message":"Registered", "user_id": user.id})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"status":"error", "message":"Invalid credentials"}), 401
    # Log successful logins to backend terminal
    print(f"[LOGIN] User {user.id} - {user.email} logged in at {datetime.utcnow().isoformat()}.")
    return jsonify({"status":"success", "user_id":user.id, "name": user.name, "is_admin": user.is_admin})

# --- API: seats & booking ---
@app.route("/api/seats", methods=["GET"])
def get_seats():
    seats = Seat.query.order_by(Seat.row, Seat.number).all()
    out = []
    for s in seats:
        out.append({
            "seat_code": s.seat_code,
            "row": s.row,
            "number": s.number,
            "status": s.status,
            "booked_by": s.booked_by
        })
    return jsonify(out)

@app.route("/api/book", methods=["POST"])
def book_seat():
    data = request.json
    user_id = data.get("user_id")
    seat_code = data.get("seat_code")
    if not user_id or not seat_code:
        return jsonify({"status":"error", "message":"Missing user_id or seat_code"}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({"status":"error", "message":"User not found"}), 400

    # Check if user already has a booking
    existing = Booking.query.filter_by(user_id=user_id).first()
    if existing:
        return jsonify({"status":"error", "message":"User already booked a seat"}), 400

    seat = Seat.query.filter_by(seat_code=seat_code).with_for_update().first()
    if not seat:
        return jsonify({"status":"error", "message":"Seat does not exist"}), 400
    if seat.status != "available":
        return jsonify({"status":"error", "message":"Seat not available"}), 400

    # mark booked
    try:
        seat.status = "booked"
        seat.booked_by = user_id
        seat.booked_at = datetime.utcnow()
        booking = Booking(user_id=user_id, seat_id=seat.id)
        db.session.add(booking)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"status":"error", "message":"Booking failed", "detail": str(e)}), 500

    return jsonify({"status":"success", "message":"Seat booked", "seat_code": seat_code})

@app.route("/api/bookings", methods=["GET"])
def get_bookings():
    user_id = request.args.get("user_id", type=int)
    if user_id:
        bookings = Booking.query.filter_by(user_id=user_id).all()
    else:
        bookings = Booking.query.all()
    out = []
    for b in bookings:
        seat = Seat.query.get(b.seat_id)
        user = User.query.get(b.user_id)
        out.append({
            "booking_id": b.id,
            "user_id": b.user_id,
            "user_name": user.name if user else None,
            "seat_code": seat.seat_code if seat else None,
            "booked_at": b.booked_at.isoformat()
        })
    return jsonify(out)

# --- API: team registration ---
@app.route("/api/register-team", methods=["POST"])
def register_team():
    data = request.json
    team_name = data.get("team_name")
    leader_name = data.get("leader_name")
    leader_email = data.get("leader_email")
    members = data.get("members")  # string or list
    category = data.get("category")
    if not team_name or not leader_name:
        return jsonify({"status":"error", "message":"team_name and leader_name required"}), 400
    team = Team(
        team_name=team_name,
        leader_name=leader_name,
        leader_email=leader_email,
        members=members if isinstance(members, str) else ",".join(members),
        category=category
    )
    db.session.add(team)
    db.session.commit()
    return jsonify({"status":"success", "message":"Team registered", "team_id": team.id})

@app.route("/api/teams", methods=["GET"])
def list_teams():
    teams = Team.query.order_by(Team.registered_at.desc()).all()
    out = []
    for t in teams:
        out.append({
            "id": t.id,
            "team_name": t.team_name,
            "leader_name": t.leader_name,
            "leader_email": t.leader_email,
            "members": t.members,
            "category": t.category,
            "status": t.status,
            "registered_at": t.registered_at.isoformat()
        })
    return jsonify(out)

@app.route("/api/teams/<int:team_id>/approve", methods=["POST"])
def approve_team(team_id):
    # for simplicity, no admin auth in demo — expect is_admin flag checked client-side or extend
    t = Team.query.get(team_id)
    if not t:
        return jsonify({"status":"error", "message":"Team not found"}), 404
    t.status = "approved"
    db.session.commit()
    return jsonify({"status":"success", "message":"Team approved"})

if __name__ == "__main__":
    # Useful for local testing; Flask will serve frontend templates & static
    app.run(host="0.0.0.0", port=5000, debug=True)
