import sys
import os
import datetime
import hashlib
import uuid
import time as _time

# Ensure current directory / persistence is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from persistence.database import engine, SessionLocal
from persistence import models

def get_password_hash(password: str):
    # Using sha256 for demo
    return hashlib.sha256(password.encode()).hexdigest()

models.Base.metadata.create_all(bind=engine)

USERS = [
    {"id": "user-admin", "name": "Admin User", "email": "admin@labreserve.test", "role": "ADMIN", "password_hash": get_password_hash("Demo@12345")},
    {"id": "user-1", "name": "Aarav Sharma", "email": "aarav.sharma@labreserve.test", "role": "STUDENT", "password_hash": get_password_hash("Demo@12345")},
    {"id": "user-2", "name": "Priya Patil", "email": "priya.patil@labreserve.test", "role": "STUDENT", "password_hash": get_password_hash("Demo@12345")},
    {"id": "user-3", "name": "Rohan Deshmukh", "email": "rohan.deshmukh@labreserve.test", "role": "STUDENT", "password_hash": get_password_hash("Demo@12345")},
    {"id": "user-4", "name": "Sneha Kulkarni", "email": "sneha.kulkarni@labreserve.test", "role": "STUDENT", "password_hash": get_password_hash("Demo@12345")},
    {"id": "user-5", "name": "Kabir Joshi", "email": "kabir.joshi@labreserve.test", "role": "STUDENT", "password_hash": get_password_hash("Demo@12345")},
]

RESOURCES = [
    {"id": "lab-a", "name": "Computer Lab A", "type": "Computer Lab", "location": "Block A, Floor 2", "capacity": 40},
    {"id": "lab-b", "name": "Computer Lab B", "type": "Computer Lab", "location": "Block B, Floor 1", "capacity": 35},
    {"id": "lab-ai", "name": "AI Research Lab", "type": "Computer Lab", "location": "Block C, Floor 3", "capacity": 25},
    {"id": "sem-1", "name": "Seminar Hall 1", "type": "Seminar Room", "location": "Main Building", "capacity": 100},
    {"id": "sem-2", "name": "Seminar Room 2", "type": "Seminar Room", "location": "Block A, Floor 1", "capacity": 40},
    {"id": "proj-1", "name": "Projector P-01", "type": "Projector", "location": "Equipment Room", "capacity": 1},
    {"id": "proj-2", "name": "Projector P-02", "type": "Projector", "location": "Equipment Room", "capacity": 1},
    {"id": "cam-1", "name": "Camera C-01", "type": "Camera", "location": "Media Lab", "capacity": 1},
    {"id": "dev-a1", "name": "Arduino Kit A-01", "type": "Development Board", "location": "Electronics Lab", "capacity": 1},
    {"id": "dev-r1", "name": "Raspberry Pi Kit R-01", "type": "Development Board", "location": "Electronics Lab", "capacity": 1},
]

db = SessionLocal()
try:
    added_users = 0
    for u in USERS:
        existing = db.query(models.User).filter_by(email=u["email"]).first()
        if not existing:
            db.add(models.User(**u))
            added_users += 1
            
    added_res = 0
    for r in RESOURCES:
        existing = db.query(models.Resource).filter_by(id=r["id"]).first()
        if not existing:
            db.add(models.Resource(**r, active=True))
            added_res += 1
            
    # Add dummy reservations (idempotent: skip if request_id already exists)
    run_ts = int(_time.time())
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    added_reserv = 0
    for i in range(15):
        req_id = f"req-seed-{run_ts}-{i}"
        existing_res = db.query(models.Reservation).filter_by(request_id=req_id).first()
        if existing_res:
            continue

        student_id = f"user-{(i % 5) + 1}"
        resource_id = RESOURCES[i % len(RESOURCES)]["id"]
        start = now + datetime.timedelta(days=i % 3, hours=i)
        end = start + datetime.timedelta(hours=1)

        res_id = str(uuid.uuid4())
        new_res = models.Reservation(
            id=res_id,
            resource_id=resource_id,
            student_id=student_id,
            start_time=start,
            end_time=end,
            status="confirmed",
            request_id=req_id,
            created_by_node="node-1",
            logical_timestamp=i
        )
        db.add(new_res)
        added_reserv += 1

    db.commit()
    print(f"[OK] Seeded {added_users} users, {added_res} resources, and {added_reserv} reservations.")
finally:
    db.close()
