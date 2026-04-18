/**
 * Dashboard Debugging Script
 * Test all navigation and functionality
 */

console.log('=== DASHBOARD DEBUGGING START ===');

// Test 1: Check if Bootstrap is loaded
if (typeof bootstrap === 'undefined') {
    console.error('❌ Bootstrap not loaded');
} else {
    console.log('✅ Bootstrap loaded');
}

// Test 2: Check if DOM elements exist
const tabs = ['overview-tab', 'scholarships-tab', 'ai-insights-tab', 'ai-assistant-tab', 'counselling-tab'];
const contents = ['overview', 'scholarships', 'ai-insights', 'ai-assistant', 'counselling'];

tabs.forEach(tabId => {
    const tabElement = document.getElementById(tabId);
    if (tabElement) {
        console.log(`✅ Tab found: ${tabId}`);
        
        // Test click event
        tabElement.addEventListener('click', function() {
            console.log(`🖱️ Tab clicked: ${tabId}`);
            
            // Find the target content
            const targetId = this.getAttribute('data-bs-target');
            console.log(`🎯 Target content: ${targetId}`);
            
            // Check if target exists
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                console.log(`✅ Target content found: ${targetId}`);
            } else {
                console.error(`❌ Target content not found: ${targetId}`);
            }
        });
    } else {
        console.error(`❌ Tab not found: ${tabId}`);
    }
});

contents.forEach(contentId => {
    const contentElement = document.getElementById(contentId);
    if (contentElement) {
        console.log(`✅ Content found: ${contentId}`);
    } else {
        console.error(`❌ Content not found: ${contentId}`);
    }
});

// Test 3: Check API endpoints
const apiEndpoints = [
    '/scholarship/api/scholarships',
    '/scholarship/api/my-applications',
    '/ai-assistant/api/chat'
];

apiEndpoints.forEach(endpoint => {
    fetch(endpoint)
        .then(response => {
            console.log(`✅ API ${endpoint} - Status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log(`✅ API ${endpoint} - Data:`, data);
        })
        .catch(error => {
            console.error(`❌ API ${endpoint} - Error:`, error);
        });
});

// Test 4: Manual tab switching
function manualTabTest(tabId, targetId) {
    console.log(`🧪 Manual test: ${tabId} -> ${targetId}`);
    
    // Hide all tabs
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('show', 'active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.nav-link').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show target tab
    const targetPane = document.querySelector(targetId);
    const targetButton = document.getElementById(tabId);
    
    if (targetPane && targetButton) {
        targetPane.classList.add('show', 'active');
        targetButton.classList.add('active');
        console.log(`✅ Manual tab switch successful`);
    } else {
        console.error(`❌ Manual tab switch failed`);
    }
}

// Test functions available globally
window.manualTabTest = manualTabTest;

console.log('=== DASHBOARD DEBUGGING END ===');
