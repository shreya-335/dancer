# run this once after installing requirements
from app import app, db
from models import Seat, User
from werkzeug.security import generate_password_hash

rows = [chr(x) for x in range(ord('A'), ord('J')+1)]  # A..J
seats_per_row = 10

with app.app_context():
    db.create_all()
    # create seats if not exist
    existing = Seat.query.first()
    if not existing:
        for r in rows:
            for n in range(1, seats_per_row+1):
                code = f"{r}{n}"
                s = Seat(seat_code=code, row=r, number=n, status="available")
                db.session.add(s)
        db.session.commit()
        print("Inserted seats.")

    # create admin user if not exists
    if not User.query.filter_by(email="admin@demo").first():
        admin = User(name="Admin", email="admin@demo", password_hash=generate_password_hash("admin123"), is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print("Created admin user: admin@demo / admin123")
    else:
        print("Admin user already exists.")
