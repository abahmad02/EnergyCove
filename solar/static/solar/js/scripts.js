// solar/static/solar/scripts.js

document.addEventListener('DOMContentLoaded', () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-visible');
            } else {
                entry.target.classList.remove('animate-visible');
            }
        });
    });

    document.querySelectorAll('.animate').forEach((section) => {
        observer.observe(section);
    });

    const navbarToggle = document.querySelector('.navbar-toggle');
    const navbarLinks = document.querySelector('.navbar-links');

    navbarToggle.addEventListener('click', () => {
        navbarLinks.classList.toggle('navbar-links-visible');
    });
});

