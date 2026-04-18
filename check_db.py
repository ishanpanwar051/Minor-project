from app import create_app
from models import db

app = create_app()

with app.app_context():
    print("Checking database tables...")
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Available tables: {tables}")
    
    if 'scholarships' not in tables:
        print("Creating scholarships table manually...")
        db.create_all()
        print("Tables created!")
