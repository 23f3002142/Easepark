# init_db.py
from models import db
from app import app  # adjust this if your app instance is named differently or lives elsewhere

with app.app_context():
    db.create_all()
    print("Database initialized.")
