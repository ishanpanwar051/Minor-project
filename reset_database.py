import os
from app import create_app, create_initial_data
from models import db
from sqlalchemy import text

def reset_db():
    app = create_app()
    with app.app_context():
        print("Attempting to reset database tables...")
        try:
            db.drop_all()
            print("Dropped all tables.")
        except Exception as e:
            print(f"Warning: Could not drop tables: {e}")
            # If drop fails, maybe we can just try to create?
            # But we want to fix schema.
            # If file is locked, we might be stuck.
        
        try:
            db.create_all()
            print("Created all tables.")
            create_initial_data()
            print("Database reset complete.")
        except Exception as e:
            print(f"Error recreating database: {e}")

if __name__ == "__main__":
    reset_db()
