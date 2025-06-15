// static/js/theme-toggle.js
document.addEventListener('DOMContentLoaded', function() {
    // Check for saved theme preference or use default
    const savedTheme = localStorage.getItem('theme') || 'dark';
    
    // Apply the saved theme
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Update toggle button state if it exists
    const toggleBtn = document.getElementById('themeToggle');
    if (toggleBtn) {
        toggleBtn.checked = savedTheme === 'light';
    }
});

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    // Save theme preference
    localStorage.setItem('theme', newTheme);
    
    // Apply new theme
    document.documentElement.setAttribute('data-theme', newTheme);
}