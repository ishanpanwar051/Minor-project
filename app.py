"""
Enhanced EduGuard Student Dropout Prevention System
Production-ready Flask application with security, ML, and comprehensive features
"""

from app_factory_enhanced import create_app
from config import Config

# Create and run the enhanced application
app = create_app()

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
