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
        
        # Test dashboard
        response = client.get('/dashboard')
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            content = response.data.decode('utf-8')
            if 'Total Students' in content:
                print('✅ Dashboard loaded successfully')
            else:
                print('❌ Dashboard content missing')
        else:
            print('❌ Dashboard error')
