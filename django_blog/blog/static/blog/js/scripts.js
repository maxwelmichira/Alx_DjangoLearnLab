// Django Blog — scripts.js

document.addEventListener('DOMContentLoaded', function () {

    // Auto-dismiss alert messages after 4 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });

    // Highlight active nav link
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.style.color = '#3498db';
            link.style.fontWeight = 'bold';
        }
    });

    console.log('Django Blog scripts loaded ✅');
});
