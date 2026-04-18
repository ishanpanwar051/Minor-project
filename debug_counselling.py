"""
Debug counselling data loading issue
"""

from app import create_app
from models import db
from sqlalchemy import text

def debug_counselling_data():
    """Debug counselling data loading"""
    app = create_app()
    
    with app.app_context():
        print("=== DEBUGGING COUNSELLING DATA ===")
        
        # Check if counselling_requests table exists
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Available tables: {tables}")
        
        if 'counselling_requests' not in tables:
            print("ERROR: counselling_requests table not found!")
            return
        
        # Check Rohit's student data
        result = db.session.execute(text("SELECT id, user_id FROM students WHERE email = 'rohit.verma@eduguard.edu'"))
        student_row = result.fetchone()
        
        if not student_row:
            print("ERROR: Rohit student not found!")
            return
        
        student_id, user_id = student_row
        print(f"Rohit's student_id: {student_id}, user_id: {user_id}")
        
        # Check counselling requests
        result = db.session.execute(text("SELECT COUNT(*) FROM counselling_requests WHERE student_id = :student_id"), {"student_id": student_id})
        count = result.fetchone()[0]
        print(f"Total counselling requests for Rohit: {count}")
        
        if count > 0:
            # Show all requests
            result = db.session.execute(text("""
                SELECT id, counselling_type, topic, description, priority, status, request_date 
                FROM counselling_requests 
                WHERE student_id = :student_id 
                ORDER BY request_date DESC
            """), {"student_id": student_id})
            
            requests = result.fetchall()
            print("Counselling requests:")
            for req in requests:
                print(f"  ID: {req[0]}, Type: {req[1]}, Topic: {req[2]}, Status: {req[5]}")
        else:
            print("No counselling requests found in database")
        
        # Test the models_enhanced import
        try:
            from models_enhanced import CounsellingRequest
            print("SUCCESS: CounsellingRequest model imported")
            
            # Try to query using the model
            requests = CounsellingRequest.query.filter_by(student_id=student_id).all()
            print(f"Model query result: {len(requests)} requests")
            
            for req in requests:
                print(f"  Model Request: {req.topic} - {req.status}")
                
        except ImportError as e:
            print(f"ERROR: Cannot import CounsellingRequest: {e}")
        except Exception as e:
            print(f"ERROR: Model query failed: {e}")

if __name__ == '__main__':
    debug_counselling_data()
