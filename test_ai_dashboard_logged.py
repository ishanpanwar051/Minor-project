from app import create_app
from flask_login import login_user
from models import User

app = create_app()

with app.app_context():
    # Get admin user
    admin = User.query.filter_by(email='admin@eduguard.edu').first()
    
    with app.test_client() as client:
        # Login first
        with client.session_transaction() as sess:
            sess['user_id'] = admin.id
            sess['_fresh'] = True
        
        # Now test AI dashboard
        response = client.get('/ai/dashboard')
        print(f'Status: {response.status_code}')
        print(f'Content length: {len(response.data)}')
        
        if response.status_code == 200:
            print('AI Dashboard loaded successfully!')
            # Check if it contains expected content
            content = response.data.decode('utf-8')
            if 'AI Dashboard' in content:
                print('✅ Page title found')
            if 'Total Students' in content:
                print('✅ Total Students card found')
            if 'At Risk Students' in content:
                print('✅ At Risk Students card found')
        else:
            print('❌ Error loading AI Dashboard')
