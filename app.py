from flask import Flask
from config import Config
from models import db, User
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes import main as main_blueprint
    from routes import auth as auth_blueprint
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)

    # Create DB Tables
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
