from app import create_app
from models import db
from models_enhanced import Scholarship, ScholarshipApplication

app = create_app()

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("Database tables created successfully!")

if __name__ == '__main__':
    init_db()
