from flask import Flask
from config import Config
from models import db, User
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Mail
    from flask_mail import Mail
    mail = Mail()
    mail.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.main_new import main_bp as main_blueprint
    from routes.auth_fixed import auth_bp as auth_blueprint
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)

    # Create DB Tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
