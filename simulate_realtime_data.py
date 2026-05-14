import time
from app import create_app
from realtime_notifications import notification_manager, socketio

def simulate_realtime_events():
    app = create_app()
    with app.app_context():
        print("🚀 Starting real-time simulation...")
        
        # 1. Simulate a general alert
        print("📢 Sending general alert...")
        notification_manager.send_alert({
            'title': 'System Update',
            'description': 'The EduGuard platform has been updated with new AI features!',
            'severity': 'info'
        })
        time.sleep(5)
        
        # 2. Simulate a high-risk alert (Targeted)
        print("⚠️ Sending high-risk alert...")
        notification_manager.send_alert({
            'title': 'Urgent Action Required',
            'description': 'Your attendance is falling below 75%. Please contact your counsellor.',
            'severity': 'High'
        }, target_role='student')
        time.sleep(5)
        
        # 3. Simulate a new scholarship posting
        print("🎓 Sending new scholarship alert...")
        notification_manager.send_alert({
            'title': 'New Scholarship Available!',
            'description': 'The "Global Tech Innovation" scholarship ($5,000) is now accepting applications.',
            'severity': 'info',
            'alert_type': 'Scholarship'
        })
        
        # 4. Simulate a dashboard refresh event
        print("🔄 Sending dashboard refresh event...")
        notification_manager.send_dashboard_update({
            'type': 'stats_refresh',
            'message': 'Refreshing dashboard statistics...'
        })
        
        print("✅ Simulation complete!")

if __name__ == "__main__":
    simulate_realtime_events()
