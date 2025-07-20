document.addEventListener('DOMContentLoaded', () => {
    // Mobile navigation toggle
    const burger = document.querySelector('.burger');
    const nav = document.querySelector('.nav-links');
    
    if (burger && nav) {
        burger.addEventListener('click', () => {
            // Toggle navigation
            nav.classList.toggle('nav-active');
            
            // Burger animation
            burger.classList.toggle('toggle');
        });
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
        if (nav && nav.classList.contains('nav-active') && !e.target.closest('.nav-links') && !e.target.closest('.burger')) {
            nav.classList.remove('nav-active');
            if (burger) burger.classList.remove('toggle');
        }
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add active class to current navigation item
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });
    
    // Scroll animations
    if ('IntersectionObserver' in window) {
        const fadeInElements = document.querySelectorAll('.fade-in');
        
        const fadeInOptions = {
            threshold: 0.1,
            rootMargin: "0px 0px -100px 0px"
        };
        
        const fadeInObserver = new IntersectionObserver((entries, fadeInObserver) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) {
                    return;
                } else {
                    entry.target.classList.add('appear');
                    fadeInObserver.unobserve(entry.target);
                }
            });
        }, fadeInOptions);
        
        fadeInElements.forEach(element => {
            fadeInObserver.observe(element);
        });
    }
    
    // Project filtering on projects page
    const filterButtons = document.querySelectorAll('.filter-btn');
    if (filterButtons.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Update active button
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Filter projects
                const filter = button.getAttribute('data-filter');
                const projectItems = document.querySelectorAll('.project-item');
                
                projectItems.forEach(item => {
                    if (filter === 'all' || item.getAttribute('data-category') === filter) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }
    
    // Contact form submission
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formStatus = document.getElementById('formStatus');
            if (formStatus) {
                formStatus.textContent = 'Sending message...';
                formStatus.className = 'form-status';
                
                // Simulate form submission (replace with actual form submission)
                setTimeout(() => {
                    formStatus.textContent = 'Your message has been sent successfully!';
                    formStatus.className = 'form-status success';
                    contactForm.reset();
                }, 1500);
            }
        });
    }
    
    // Admin image preview
    const imageInput = document.getElementById('image');
    const imagePreview = document.getElementById('imagePreview');
    
    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                }
                reader.readAsDataURL(file);
            }
        });
    }
});
