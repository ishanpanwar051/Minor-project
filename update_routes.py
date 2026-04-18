"""
Daily Update Routes for EduGuard
Attendance aur User Data ka daily automatic update API endpoints
"""

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from models import db
from sqlalchemy import text
from datetime import datetime, date
# Imports will be done inside functions to avoid circular import
import threading

update_bp = Blueprint('update', __name__, url_prefix='/update')

@update_bp.route('/status')
@login_required
def update_status():
    """Get current update status"""
    try:
        from daily_update_system import get_update_status
        status = get_update_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@update_bp.route('/manual', methods=['POST'])
@login_required
def manual_update():
    """Force manual update now"""
    try:
        # Check if user has permission (admin or faculty)
        if current_user.role not in ['admin', 'faculty']:
            return jsonify({
                'success': False,
                'error': 'Permission denied'
            }), 403
        
        # Run manual update in background thread
        def run_update():
            from daily_update_system import manual_update_now
            manual_update_now()
        
        update_thread = threading.Thread(target=run_update, daemon=True)
        update_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Manual update started in background'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@update_bp.route('/start')
@login_required
def start_updates():
    """Start daily update system"""
    try:
        # Check if user has permission
        if current_user.role not in ['admin', 'faculty']:
            return jsonify({
                'success': False,
                'error': 'Permission denied'
            }), 403
        
        from daily_update_system import start_daily_updates
        start_daily_updates()
        
        return jsonify({
            'success': True,
            'message': 'Daily update system started'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@update_bp.route('/stop')
@login_required
def stop_updates():
    """Stop daily update system"""
    try:
        # Check if user has permission
        if current_user.role not in ['admin', 'faculty']:
            return jsonify({
                'success': False,
                'error': 'Permission denied'
            }), 403
        
        from daily_update_system import stop_daily_updates
        stop_daily_updates()
        
        return jsonify({
            'success': True,
            'message': 'Daily update system stopped'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@update_bp.route('/attendance')
@login_required
def attendance_update():
    """Update attendance only"""
    try:
        # Check if user has permission
        if current_user.role not in ['admin', 'faculty']:
            return jsonify({
                'success': False,
                'error': 'Permission denied'
            }), 403
        
        from daily_update_system import DailyUpdateSystem
        updater = DailyUpdateSystem()
        
        def run_attendance_update():
            with updater.app.app_context():
                updater.update_daily_attendance()
        
        update_thread = threading.Thread(target=run_attendance_update, daemon=True)
        update_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Attendance update started'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@update_bp.route('/user-data')
@login_required
def user_data_update():
    """Update user data only"""
    try:
        # Check if user has permission
        if current_user.role not in ['admin', 'faculty']:
            return jsonify({
                'success': False,
                'error': 'Permission denied'
            }), 403
        
        from daily_update_system import DailyUpdateSystem
        updater = DailyUpdateSystem()
        
        def run_user_update():
            with updater.app.app_context():
                updater.update_user_data()
        
        update_thread = threading.Thread(target=run_user_update, daemon=True)
        update_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'User data update started'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@update_bp.route('/dashboard')
@login_required
def update_dashboard():
    """Update dashboard page"""
    try:
        # Check if user has permission
        if current_user.role not in ['admin', 'faculty']:
            return jsonify({
                'success': False,
                'error': 'Permission denied'
            }), 403
        
        return render_template('admin/update_dashboard.html')
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API endpoints for frontend
@update_bp.route('/api/attendance-stats')
@login_required
def attendance_stats():
    """Get attendance statistics"""
    try:
        query = text("""
            SELECT date, 
                   COUNT(*) as total_students,
                   SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_students,
                   SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent_students,
                   SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) as late_students
            FROM attendance 
            WHERE date >= date('now', '-7 days')
            GROUP BY date
            ORDER BY date DESC
        """)
        
        result = db.session.execute(query)
        stats = []
        
        for row in result:
            stats.append({
                'date': row[0],
                'total_students': row[1],
                'present_students': row[2],
                'absent_students': row[3],
                'late_students': row[4],
                'attendance_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0
            })
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@update_bp.route('/api/user-stats')
@login_required
def user_stats():
    """Get user statistics"""
    try:
        query = text("""
            SELECT 
                COUNT(*) as total_users,
                SUM(CASE WHEN role = 'student' THEN 1 ELSE 0 END) as students,
                SUM(CASE WHEN role = 'faculty' THEN 1 ELSE 0 END) as faculty,
                SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as admins,
                MAX(updated_at) as last_update
            FROM users
        """)
        
        result = db.session.execute(query)
        stats = result.fetchone()
        
        return jsonify({
            'success': True,
            'data': {
                'total_users': stats[0],
                'students': stats[1],
                'faculty': stats[2],
                'admins': stats[3],
                'last_update': stats[4]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
