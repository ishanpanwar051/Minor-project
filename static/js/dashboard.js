/**
 * Student Dashboard JavaScript
 * Handles dynamic data loading and UI interactions
 */

console.log('[FRONTEND] Dashboard script loaded');

// Dynamic Data Loading
function loadScholarshipData() {
    console.log('[FRONTEND] Loading scholarship data...');
    
    // Load available scholarships
    fetch('/scholarship/api/scholarships')
        .then(response => {
            console.log('[FRONTEND] Scholarships API response:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('[FRONTEND] Scholarships data received:', data);
            if (data.success) {
                updateScholarshipsList(data.data);
            } else {
                console.error('[FRONTEND] Scholarships API error:', data.error);
                showErrorMessage('Failed to load scholarships: ' + data.error);
            }
        })
        .catch(error => {
            console.error('[FRONTEND] Scholarships fetch error:', error);
            showErrorMessage('Network error loading scholarships');
        });
    
    // Load student applications
    fetch('/scholarship/api/my-applications')
        .then(response => {
            console.log('[FRONTEND] Applications API response:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('[FRONTEND] Applications data received:', data);
            if (data.success) {
                updateApplicationsList(data.data);
                updateApplicationCount(data.count);
            } else {
                console.error('[FRONTEND] Applications API error:', data.error);
                showErrorMessage('Failed to load applications: ' + data.error);
            }
        })
        .catch(error => {
            console.error('[FRONTEND] Applications fetch error:', error);
            showErrorMessage('Network error loading applications');
        });
}

function updateScholarshipsList(scholarships) {
    const container = document.getElementById('scholarshipsList');
    if (!container) return;
    
    if (scholarships.length === 0) {
        container.innerHTML = '<p class="text-muted">No scholarships available</p>';
        return;
    }
    
    container.innerHTML = scholarships.map(scholarship => {
        return '<div class="card mb-3 scholarship-card">' +
            '<div class="card-body">' +
                '<div class="row align-items-center">' +
                    '<div class="col-md-8">' +
                        '<h6 class="card-title">' + scholarship.title + '</h6>' +
                        '<p class="card-text text-muted">' + scholarship.description + '</p>' +
                        '<div class="d-flex gap-2">' +
                            '<span class="badge bg-primary">$' + scholarship.amount + '</span>' +
                            '<span class="badge bg-info">Min GPA: ' + (scholarship.min_gpa || 'N/A') + '</span>' +
                        '</div>' +
                    '</div>' +
                    '<div class="col-md-4 text-end">' +
                        '<button class="btn btn-success apply-btn" onclick="applyForScholarship(' + scholarship.id + ')">' +
                            '<i class="fas fa-paper-plane"></i> Apply' +
                        '</button>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>';
    }).join('');
}

function updateApplicationsList(applications) {
    const container = document.getElementById('recentApplications');
    if (!container) return;
    
    if (applications.length === 0) {
        container.innerHTML = '<p class="text-muted">No applications yet</p>';
        return;
    }
    
    container.innerHTML = applications.slice(0, 3).map(app => {
        return '<div class="d-flex justify-content-between align-items-center mb-3">' +
            '<div>' +
                '<strong>' + app.scholarship_title + '</strong>' +
                '<br><small class="text-muted">' + new Date(app.application_date).toLocaleDateString() + '</small>' +
            '</div>' +
            '<span class="badge bg-' + getStatusColor(app.status) + '">' + app.status + '</span>' +
        '</div>';
    }).join('');
}

function updateApplicationCount(count) {
    const countElement = document.getElementById('applicationCount');
    if (countElement) {
        countElement.textContent = count;
    }
}

function getStatusColor(status) {
    const colors = {
        'approved': 'success',
        'pending': 'warning',
        'rejected': 'danger'
    };
    return colors[status] || 'secondary';
}

function applyForScholarship(scholarshipId) {
    console.log('[FRONTEND] Applying for scholarship:', scholarshipId);
    
    // Check eligibility first
    fetch('/scholarship/api/eligibility/' + scholarshipId)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.eligible) {
                    // Redirect to application page
                    window.location.href = '/scholarship/apply/' + scholarshipId;
                } else {
                    alert('Not eligible: ' + data.reasons.join(', '));
                }
            } else {
                alert('Error checking eligibility: ' + data.error);
            }
        })
        .catch(error => {
            console.error('[FRONTEND] Eligibility check error:', error);
            alert('Network error checking eligibility');
        });
}

function showErrorMessage(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = 
        message +
        '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
    
    const container = document.querySelector('.container-fluid');
    if (container) {
        container.prepend(alertDiv);
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Chat functionality
function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    const chatContainer = document.getElementById('chatContainer');
    
    // Add user message
    const userMsg = document.createElement('div');
    userMsg.className = 'chat-message user-message';
    userMsg.innerHTML = '<strong>You:</strong> ' + message;
    chatContainer.appendChild(userMsg);
    
    // Clear input
    input.value = '';
    
    // Show typing indicator
    const typingMsg = document.createElement('div');
    typingMsg.className = 'chat-message ai-message';
    typingMsg.id = 'typingIndicator';
    typingMsg.innerHTML = '<strong>AI Assistant:</strong> <em>Thinking...</em>';
    chatContainer.appendChild(typingMsg);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // Try AI Assistant endpoint first, fallback to simple chat
    fetch('/ai-assistant/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => {
        if (!response.ok) throw new Error('AI Assistant unavailable');
        return response.json();
    })
    .then(data => {
        // Remove typing indicator
        const typing = document.getElementById('typingIndicator');
        if (typing) typing.remove();
        
        // Add AI response
        const aiMsg = document.createElement('div');
        aiMsg.className = 'chat-message ai-message';
        let responseText = data.response || 'Sorry, I could not process your request.';
        aiMsg.innerHTML = '<strong>AI Assistant:</strong> ' + responseText;
        chatContainer.appendChild(aiMsg);
        
        // Add suggestion buttons if available
        if (data.suggestions && data.suggestions.length > 0) {
            const suggestionsDiv = document.createElement('div');
            suggestionsDiv.className = 'mt-2 d-flex flex-wrap gap-1';
            data.suggestions.forEach(function(suggestion) {
                const btn = document.createElement('button');
                btn.className = 'btn btn-outline-primary btn-sm';
                btn.textContent = suggestion;
                btn.onclick = function() {
                    document.getElementById('chatInput').value = suggestion;
                    sendMessage();
                };
                suggestionsDiv.appendChild(btn);
            });
            chatContainer.appendChild(suggestionsDiv);
        }
        
        chatContainer.scrollTop = chatContainer.scrollHeight;
    })
    .catch(error => {
        console.warn('[FRONTEND] AI Assistant failed, trying fallback:', error);
        
        // Fallback to simple chat endpoint
        const formData = new FormData();
        formData.append('message', message);
        
        fetch('/ai/chat_response', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            const typing = document.getElementById('typingIndicator');
            if (typing) typing.remove();
            
            const aiMsg = document.createElement('div');
            aiMsg.className = 'chat-message ai-message';
            aiMsg.innerHTML = '<strong>AI Assistant:</strong> ' + (data.response || 'Sorry, I could not process your request.');
            chatContainer.appendChild(aiMsg);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        })
        .catch(err => {
            console.error('[FRONTEND] Both chat endpoints failed:', err);
            const typing = document.getElementById('typingIndicator');
            if (typing) typing.remove();
            
            const errorMsg = document.createElement('div');
            errorMsg.className = 'chat-message ai-message';
            errorMsg.innerHTML = '<strong>AI Assistant:</strong> I\'m here to help! You can ask me about study strategies, stress management, career guidance, motivation, or time management.';
            chatContainer.appendChild(errorMsg);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        });
    });
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('[FRONTEND] Dashboard loaded');
    
    // Initialize charts
    initializeCharts();
    
    // Load dynamic data
    loadScholarshipData();
    
    // Set up chat input event listener
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
});

// Initialize charts using data attributes
function initializeCharts() {
    const chartDataElement = document.getElementById('chartData');
    if (!chartDataElement) return;
    
    const avgSuccessProb = parseFloat(chartDataElement.dataset.avgSuccessProb) || 0;
    const remainingProb = parseFloat(chartDataElement.dataset.remainingProb) || 0;
    const studentGpa = parseFloat(chartDataElement.dataset.studentGpa) || 3.5;
    
    console.log('[FRONTEND] Initializing charts with data:', { avgSuccessProb, remainingProb, studentGpa });
    
    // Progress Chart
    const progressCtx = document.getElementById('progressChart');
    if (progressCtx && typeof Chart !== 'undefined') {
        new Chart(progressCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [avgSuccessProb, remainingProb],
                    backgroundColor: ['#667eea', '#e0e0e0'],
                    borderWidth: 0
                }]
            },
            options: {
                cutout: '70%',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            }
        });
    }

    // Performance Chart
    const performanceCtx = document.getElementById('performanceChart');
    if (performanceCtx && typeof Chart !== 'undefined') {
        new Chart(performanceCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'GPA Trend',
                    data: [3.2, 3.4, 3.3, 3.5, 3.6, studentGpa],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 2.5,
                        max: 4.0
                    }
                }
            }
        });
    }
}

// Tab switching function
function switchTab(tabName) {
    console.log(`[FRONTEND] Switching to tab: ${tabName}`);
    
    // Hide all tab panes
    const allPanes = document.querySelectorAll('.tab-pane');
    allPanes.forEach(pane => {
        pane.classList.remove('show', 'active');
    });
    
    // Remove active class from all nav buttons
    const allButtons = document.querySelectorAll('.nav-link');
    allButtons.forEach(button => {
        button.classList.remove('active');
    });
    
    // Show target tab
    const targetPane = document.getElementById(tabName);
    const targetButton = document.querySelector(`[data-bs-target="#${tabName}"]`);
    
    if (targetPane && targetButton) {
        targetPane.classList.add('show', 'active');
        targetButton.classList.add('active');
        console.log(`[FRONTEND] Successfully switched to ${tabName} tab`);
        
        // Load tab-specific data
        if (tabName === 'scholarships') {
            loadScholarshipData();
        }
    } else {
        console.error(`[FRONTEND] Target tab not found: ${tabName}`);
    }
}

// Make functions globally available
window.loadScholarshipData = loadScholarshipData;
window.applyForScholarship = applyForScholarship;
window.sendMessage = sendMessage;
window.switchTab = switchTab;
