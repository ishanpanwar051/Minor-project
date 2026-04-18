from app import create_app

app = create_app()

with app.test_client() as client:
    response = client.get('/ai/dashboard')
    print(f'Status: {response.status_code}')
    print(f'Content length: {len(response.data)}')
    if response.status_code == 500:
        print('Error occurred')
    else:
        print('Page loaded successfully')
