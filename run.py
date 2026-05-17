from app import create_app
import os

app = create_app(os.getenv('FLASK_CONFIG', 'default'))
app.config['SQLALCHEMY_ECHO'] = os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true'

if __name__ == '__main__':
    debug_mode = app.config.get('DEBUG', False)
    app.run(
        host=os.getenv('HOST', '127.0.0.1'),
        port=int(os.getenv('PORT', '5000')),
        debug=debug_mode,
        use_reloader=False
    )
