import os

os.environ.setdefault('FLASK_CONFIG', 'production')

from app import create_app, create_initial_data

app = create_app(os.getenv('FLASK_CONFIG', 'production'))

with app.app_context():
    create_initial_data()
