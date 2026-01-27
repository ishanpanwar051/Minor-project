from flask_migrate import Migrate
from app_factory import create_app
from models import db, User, Student, Attendance, AcademicRecord, Intervention, RiskProfile
from utils import batch_update_risk_scores
from email_service import send_weekly_digest
import click
from datetime import datetime
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.cli.command()
@click.option('--count', default=50, help='Number of sample students to create')
def seed_db(count):
    """Seed the database with sample data."""
    from seed_data import seed_database
    seed_database()
    click.echo(f'Database seeded with {count} sample students!')

@app.cli.command()
def update_risks():
    """Update risk scores for all students."""
    count = batch_update_risk_scores()
    click.echo(f'Updated risk scores for {count} students.')

@app.cli.command()
def send_digest():
    """Send weekly digest email to all faculty."""
    from email_service import send_weekly_digest
    success = send_weekly_digest()
    if success:
        click.echo('Weekly digest sent successfully!')
    else:
        click.echo('Failed to send weekly digest.')

@app.cli.command()
@click.option('--email', required=True, help='Email address for the admin user')
@click.option('--password', default='admin123', help='Password for the admin user')
def create_admin(email, password):
    """Create an admin user."""
    admin = User.query.filter_by(email=email).first()
    if admin:
        click.echo('Admin user already exists!')
        return
    
    admin = User(
        username='admin',
        email=email,
        role='admin'
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    click.echo(f'Admin user created with email: {email}')

@app.cli.command()
def backup_db():
    """Create a backup of the database."""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'backup_dropout_prevention_{timestamp}.db'
    
    try:
        shutil.copy2('dropout_prevention.db', backup_path)
        click.echo(f'Database backed up to: {backup_path}')
    except Exception as e:
        click.echo(f'Backup failed: {str(e)}')

@app.cli.command()
def cleanup_logs():
    """Clean up old log files."""
    import glob
    import os
    from datetime import datetime, timedelta
    
    log_files = glob.glob('logs/*.log*')
    cutoff_date = datetime.now() - timedelta(days=30)
    
    for log_file in log_files:
        file_time = datetime.fromtimestamp(os.path.getctime(log_file))
        if file_time < cutoff_date:
            os.remove(log_file)
            click.echo(f'Removed old log file: {log_file}')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
