"""
Real-time Notification System for EduGuard
Provides WebSocket-based real-time alerts and updates
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')

class NotificationManager:
    """Manages real-time notifications and alerts"""
    
    def __init__(self):
        self.active_users = {}
        self.notification_queue = []
    
    def register_user(self, user_id, session_id):
        """Register a user for real-time notifications"""
        self.active_users[user_id] = {
            'session_id': session_id,
            'last_seen': datetime.utcnow(),
            'role': getattr(current_user, 'role', 'unknown') if current_user else 'unknown'
        }
        logger.info(f"User {user_id} registered for notifications")
    
    def unregister_user(self, user_id):
        """Unregister a user from notifications"""
        if user_id in self.active_users:
            del self.active_users[user_id]
            logger.info(f"User {user_id} unregistered from notifications")
    
    def send_alert(self, alert_data, target_role=None, target_user=None):
        """Send real-time alert to users"""
        notification = {
            'type': 'alert',
            'data': alert_data,
            'timestamp': datetime.utcnow().isoformat(),
            'id': len(self.notification_queue) + 1
        }
        
        if target_user:
            # Send to specific user
            socketio.emit('notification', notification, room=f"user_{target_user}")
        elif target_role:
            # Send to all users with specific role
            for user_id, user_info in self.active_users.items():
                if user_info.get('role') == target_role:
                    socketio.emit('notification', notification, room=f"user_{user_id}")
        else:
            # Send to all active users
            socketio.emit('notification', notification, broadcast=True)
        
        self.notification_queue.append(notification)
        logger.info(f"Alert sent: {alert_data.get('title', 'Unknown')}")
    
    def send_dashboard_update(self, update_data):
        """Send dashboard update to all active users"""
        update = {
            'type': 'dashboard_update',
            'data': update_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        socketio.emit('dashboard_update', update, broadcast=True)
        logger.info("Dashboard update sent to all users")
    
    def send_risk_level_change(self, student_data, old_level, new_level):
        """Send notification when student risk level changes"""
        alert_data = {
            'title': f'Risk Level Changed: {student_data["first_name"]} {student_data["last_name"]}',
            'description': f'Risk level changed from {old_level} to {new_level}',
            'severity': new_level,
            'student_id': student_data['student_id'],
            'alert_type': 'Risk Level Change'
        }
        
        # Send to faculty and admin
        self.send_alert(alert_data, target_role='faculty')
        self.send_alert(alert_data, target_role='admin')
    
    def send_attendance_alert(self, student_data, attendance_rate):
        """Send attendance alert"""
        if attendance_rate < 60:
            severity = 'Critical'
        elif attendance_rate < 75:
            severity = 'High'
        else:
            severity = 'Medium'
        
        alert_data = {
            'title': f'Attendance Alert: {student_data["first_name"]} {student_data["last_name"]}',
            'description': f'Attendance rate: {attendance_rate:.1f}%',
            'severity': severity,
            'student_id': student_data['student_id'],
            'alert_type': 'Attendance'
        }
        
        self.send_alert(alert_data, target_role='faculty')
    
    def send_academic_alert(self, student_data, academic_performance):
        """Send academic performance alert"""
        if academic_performance < 30:
            severity = 'Critical'
        elif academic_performance < 40:
            severity = 'High'
        else:
            severity = 'Medium'
        
        alert_data = {
            'title': f'Academic Alert: {student_data["first_name"]} {student_data["last_name"]}',
            'description': f'Academic performance: {academic_performance:.1f}%',
            'severity': severity,
            'student_id': student_data['student_id'],
            'alert_type': 'Academic Performance'
        }
        
        self.send_alert(alert_data, target_role='faculty')

# Global notification manager
notification_manager = NotificationManager()

# SocketIO event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    if current_user.is_authenticated:
        user_id = current_user.id
        session_id = request.sid
        
        # Register user for notifications
        notification_manager.register_user(user_id, session_id)
        
        # Join user-specific room
        join_room(f"user_{user_id}")
        
        # Join role-based room
        if hasattr(current_user, 'role'):
            join_room(f"role_{current_user.role}")
        
        emit('connected', {
            'status': 'connected',
            'user_id': user_id,
            'role': getattr(current_user, 'role', 'unknown')
        })
        
        logger.info(f"Client connected: {user_id}")
    else:
        emit('error', {'message': 'Authentication required'})
        return False

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    if current_user.is_authenticated:
        user_id = current_user.id
        
        # Leave rooms
        leave_room(f"user_{user_id}")
        if hasattr(current_user, 'role'):
            leave_room(f"role_{current_user.role}")
        
        # Unregister user
        notification_manager.unregister_user(user_id)
        
        logger.info(f"Client disconnected: {user_id}")

@socketio.on('join_dashboard')
def handle_join_dashboard():
    """Handle joining dashboard room for real-time updates"""
    if current_user.is_authenticated:
        join_room('dashboard')
        emit('joined_dashboard', {'status': 'joined'})

@socketio.on('leave_dashboard')
def handle_leave_dashboard():
    """Handle leaving dashboard room"""
    if current_user.is_authenticated:
        leave_room('dashboard')
        emit('left_dashboard', {'status': 'left'})

@socketio.on('request_alerts')
def handle_request_alerts():
    """Handle request for recent alerts"""
    if current_user.is_authenticated:
        try:
            from models import Alert, db
            
            # Get recent alerts based on user role
            if current_user.role in ['admin', 'faculty']:
                alerts = Alert.query.order_by(Alert.created_at.desc()).limit(10).all()
            else:
                # Students only see their own alerts
                alerts = Alert.query.join(Student).filter(
                    Student.user_id == current_user.id
                ).order_by(Alert.created_at.desc()).limit(10).all()
            
            alerts_data = []
            for alert in alerts:
                alerts_data.append({
                    'id': alert.id,
                    'title': alert.title,
                    'description': alert.description,
                    'severity': alert.severity,
                    'alert_type': alert.alert_type,
                    'created_at': alert.created_at.isoformat() if alert.created_at else None,
                    'status': alert.status
                })
            
            emit('alerts_response', {'alerts': alerts_data})
            
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            emit('error', {'message': 'Failed to fetch alerts'})

def init_realtime_notifications(app):
    """Initialize real-time notification system"""
    socketio.init_app(app)
    logger.info("Real-time notification system initialized")
    return socketio
