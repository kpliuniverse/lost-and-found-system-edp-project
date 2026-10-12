"""Optional: fill the database with a few sample posts.  Run:  python seed.py"""
from datetime import date, timedelta

from app.database import Base, SessionLocal, engine
from app.models import Item
from app.security import hash_pin

Base.metadata.create_all(bind=engine)
today = date.today()

samples = [
    ("lost", "Black leather wallet", "Wallets & cards", "Brown stitching, has a student ID inside.", "Main library, 2nd floor", 1, "Mara", "mara@example.com"),
    ("found", "Set of three keys on a blue ring", "Keys", "Found on a bench. One key has a red cap.", "City Park, near the fountain", 2, "Joel", "0917 000 1111"),
    ("lost", "Grey tabby cat named Biscuit", "Pets", "Wearing a green collar. Very friendly.", "Rizal Street", 3, "Ana", "ana@example.com"),
    ("found", "Silver phone with cracked corner", "Phones & electronics", "Lock screen shows a mountain photo.", "Bus stop, Route 12", 0, "Sam", "sam@example.com"),
]

with SessionLocal() as db:
    for status, title, cat, desc, loc, days_ago, name, contact in samples:
        db.add(Item(
            status=status, title=title, category=cat, description=desc, location=loc,
            event_date=today - timedelta(days=days_ago),
            contact_name=name, contact_info=contact, pin_hash=hash_pin("1234"),
        ))
    db.commit()

print("Added", len(samples), "sample posts. Their PIN is 1234.")
