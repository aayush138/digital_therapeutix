from app.models.user import User
from app.extensions import db
from app.seed.seed_data import create_dummy_data

def seed_database():
    if not User.query.first():
        print("🔄 Seeding DB with dummy data...")
        create_dummy_data()
        db.session.commit()
        print("✅ Seed completed.")
    else:
        print("✅ Seed skipped — data already exists.")