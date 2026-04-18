/**
 * Real-time Updates for EduGuard
 * Handles WebSocket connections and live data updates
 */

class RealtimeUpdates {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        
        this.init();
    }
    
    init() {
        if (typeof io === 'undefined') {
            console.error('Socket.IO not loaded');
            return;
        }
        
        this.connect();
        
        // Auto-refresh dashboard data every 30 seconds
        setInterval(() => {
            this.refreshDashboardData();
        }, 30000);
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.disconnect();
            } else {
                this.connect();
            }
        });
    }
    
    connect() {
        if (this.socket && this.connected) {
            return;
        }
        
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to real-time server');
            this.connected = true;
            this.reconnectAttempts = 0;
            
            // Join dashboard room for updates
            this.socket.emit('join_dashboard');
            
            // Request initial alerts
            this.socket.emit('request_alerts');
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from real-time server');
            this.connected = false;
            this.attemptReconnect();
        });
        
        this.socket.on('notification', (data) => {
            this.handleNotification(data);
        });
        
        this.socket.on('dashboard_update', (data) => {
            this.handleDashboardUpdate(data);
        });
        
        this.socket.on('alerts_response', (data) => {
            this.handleAlertsResponse(data);
        });
        
        this.socket.on('connected', (data) => {
            console.log('User connected:', data);
        });
        
        this.socket.on('error', (error) => {
            console.error('Socket error:', error);
        });
    }
    
    disconnect() {
        if (this.socket) {
            this.socket.emit('leave_dashboard');
            this.socket.disconnect();
            this.socket = null;
            this.connected = false;
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            return;
        }
        
        this.reconnectAttempts++;
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        setTimeout(() => {
            this.connect();
        }, this.reconnectDelay * this.reconnectAttempts);
    }
    
    handleNotification(data) {
        console.log('Received notification:', data);
        
        // Show notification toast
        this.showNotificationToast(data);
        
        // Update alerts section if exists
        this.updateAlertsSection(data);
        
        // Play notification sound (optional)
        this.playNotificationSound(data.severity);
    }
    
    handleDashboardUpdate(data) {
        console.log('Received dashboard update:', data);
        
        // Update statistics cards
        this.updateStatisticsCards(data);
        
        // Update charts if they exist
        this.updateCharts(data);
        
        // Update student lists
        this.updateStudentLists(data);
    }
    
    handleAlertsResponse(data) {
        console.log('Received alerts response:', data);
        this.updateAlertsSection(data);
    }
    
    showNotificationToast(notification) {
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${this.getSeverityColor(notification.severity)} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${notification.title}</strong><br>
                    <small>${notification.description}</small>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1050';
        document.body.appendChild(container);
        return container;
    }
    
    getSeverityColor(severity) {
        switch (severity.toLowerCase()) {
            case 'critical': return 'danger';
            case 'high': return 'warning';
            case 'medium': return 'info';
            case 'low': return 'success';
            default: return 'primary';
        }
    }
    
    updateAlertsSection(data) {
        const alertsContainer = document.getElementById('alertsContainer');
        if (!alertsContainer) return;
        
        if (data.alerts && Array.isArray(data.alerts)) {
            alertsContainer.innerHTML = '';
            data.alerts.forEach(alert => {
                const alertElement = this.createAlertElement(alert);
                alertsContainer.appendChild(alertElement);
            });
        } else if (data.data) {
            // Single notification
            const alertElement = this.createAlertElement(data.data);
            alertsContainer.insertBefore(alertElement, alertsContainer.firstChild);
        }
    }
    
    createAlertElement(alert) {
        const div = document.createElement('div');
        div.className = `alert alert-${this.getSeverityColor(alert.severity)} alert-dismissible fade show`;
        div.innerHTML = `
            <h6 class="alert-heading">${alert.title}</h6>
            <p class="mb-1">${alert.description}</p>
            <small class="text-muted">${this.formatDate(alert.created_at || alert.timestamp)}</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        return div;
    }
    
    updateStatisticsCards(data) {
        // Update total students
        if (data.total_students !== undefined) {
            this.updateCardValue('totalStudents', data.total_students);
        }
        
        // Update at-risk students
        if (data.at_risk_students !== undefined) {
            this.updateCardValue('atRiskStudents', data.at_risk_students);
        }
        
        // Update attendance rate
        if (data.avg_attendance !== undefined) {
            this.updateCardValue('avgAttendance', data.avg_attendance + '%');
        }
        
        // Update GPA
        if (data.avg_gpa !== undefined) {
            this.updateCardValue('avgGpa', data.avg_gpa);
        }
    }
    
    updateCardValue(cardId, value) {
        const card = document.getElementById(cardId);
        if (card) {
            card.textContent = value;
            // Add animation
            card.classList.add('text-primary');
            setTimeout(() => {
                card.classList.remove('text-primary');
            }, 1000);
        }
    }
    
    updateCharts(data) {
        // Update risk distribution chart
        if (data.risk_stats && window.riskChart) {
            window.riskChart.data.datasets[0].data = [
                data.risk_stats.low,
                data.risk_stats.medium,
                data.risk_stats.high,
                data.risk_stats.critical
            ];
            window.riskChart.update();
        }
        
        // Update attendance chart
        if (data.attendance_data && window.attendanceChart) {
            window.attendanceChart.data.datasets[0].data = data.attendance_data;
            window.attendanceChart.update();
        }
    }
    
    updateStudentLists(data) {
        // Update risky students list
        if (data.risky_students && document.getElementById('riskyStudentsList')) {
            const listContainer = document.getElementById('riskyStudentsList');
            listContainer.innerHTML = '';
            
            data.risky_students.forEach(student => {
                const listItem = this.createStudentListItem(student);
                listContainer.appendChild(listItem);
            });
        }
    }
    
    createStudentListItem(student) {
        const div = document.createElement('div');
        div.className = 'col-md-6 mb-3';
        div.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h6 class="card-title">${student.first_name} ${student.last_name}</h6>
                    <p class="card-text">
                        <small class="text-muted">ID: ${student.student_id}</small><br>
                        <span class="badge bg-${this.getSeverityColor(student.risk_level)}">${student.risk_level}</span>
                        <span class="badge bg-secondary">Score: ${student.risk_score}</span>
                    </p>
                </div>
            </div>
        `;
        return div;
    }
    
    refreshDashboardData() {
        if (!this.connected) return;
        
        // Request fresh data from server
        fetch('/api/dashboard_stats')
            .then(response => response.json())
            .then(data => {
                this.handleDashboardUpdate(data);
            })
            .catch(error => {
                console.error('Error refreshing dashboard:', error);
            });
    }
    
    playNotificationSound(severity) {
        if (severity === 'critical' || severity === 'high') {
            // Play sound for critical alerts
            const audio = new Audio('/static/sounds/alert.mp3');
            audio.volume = 0.3;
            audio.play().catch(e => console.log('Could not play sound:', e));
        }
    }
    
    formatDate(dateString) {
        if (!dateString) return 'Just now';
        
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} minutes ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;
        
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
}

// Initialize real-time updates when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.realtimeUpdates = new RealtimeUpdates();
});

// Export for use in other scripts
window.RealtimeUpdates = RealtimeUpdates;
