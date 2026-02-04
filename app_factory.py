from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_talisman import Talisman
from flask_migrate import Migrate
from config_ews import get_config
from models_ews import db, User

# Initialize extensions
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
mail = Mail()
migrate = Migrate()
talisman = Talisman()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load config
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    
    # Talisman only in prod usually, or strict mode
    if app.config.get('SESSION_COOKIE_SECURE'):
        talisman.init_app(app, force_https=True)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    # Register Blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.parent import parent_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(parent_bp, url_prefix='/parent')
    
    # CLI Commands
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()
        # Create default admin if passed in environment or just print
        print("Database tables created.")

    @app.cli.command()
    def seed_db():
        """Seed the database with sample data."""
        from models_ews import User, Student, UserRole
        import random
        from werkzeug.security import generate_password_hash
        
        # Create Admin
        if not User.query.filter_by(email='admin@college.edu').first():
            admin = User(
                username='admin',
                email='admin@college.edu',
                role=UserRole.ADMIN,
                first_name='Admin',
                last_name='User'
            )
            admin.set_password('password')
            db.session.add(admin)
            print("Created admin@college.edu / password")
            
        # Create Parent
        if not User.query.filter_by(email='parent@home.com').first():
            parent = User(
                username='parent',
                email='parent@home.com',
                role=UserRole.PARENT,
                first_name='Parent',
                last_name='Guardian'
            )
            parent.set_password('password')
            db.session.add(parent)
            print("Created parent@home.com / password")
            
        db.session.commit()
        print("Database seeded.")
        
    @app.cli.command()
    def run_ml_training():
        """Train the ML model on synthetic data."""
        from services.ml_service import ml_service
        result = ml_service.train_model()
        if result['success']:
            print(f"Model trained. Accuracy: {result['accuracy']:.2f}")
        else:
            print("Model training failed.")
            
    return app
