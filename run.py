from app import create_app
import os

app = create_app(os.getenv('FLASK_CONFIG', 'default'))

if __name__ == '__main__':
    debug_mode = app.config.get('DEBUG', False)
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=debug_mode,
        use_reloader=False
    )
