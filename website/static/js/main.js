// Enhanced carousel functionality
function initCarousel(carouselId) {
    const carousel = document.getElementById(carouselId);
    if (!carousel) return;
    
    const images = carousel.querySelectorAll('.carousel-images');
    let currentIndex = 0;
    let autoSlideInterval;

    // Create indicators
    const indicatorsContainer = document.createElement('div');
    indicatorsContainer.className = 'carousel-indicators';
    
    images.forEach((_, index) => {
        const indicator = document.createElement('div');
        indicator.className = 'carousel-indicator';
        if (index === 0) indicator.classList.add('active');
        indicator.onclick = () => goToSlide(index);
        indicatorsContainer.appendChild(indicator);
    });
    
    if (images.length > 1) {
        carousel.appendChild(indicatorsContainer);
    }

    function showImage(index) {
        images.forEach((img, i) => {
            img.classList.remove('active');
            const indicator = indicatorsContainer.children[i];
            if (indicator) indicator.classList.remove('active');
        });
        
        if (images[index]) {
            images[index].classList.add('active');
            const indicator = indicatorsContainer.children[index];
            if (indicator) indicator.classList.add('active');
        }
    }

    function nextImage() {
        currentIndex = (currentIndex + 1) % images.length;
        showImage(currentIndex);
    }

    function prevImage() {
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        showImage(currentIndex);
    }

    function goToSlide(index) {
        currentIndex = index;
        showImage(currentIndex);
        resetAutoSlide();
    }

    function startAutoSlide() {
        if (images.length > 1) {
            autoSlideInterval = setInterval(nextImage, 5000);
        }
    }

    function resetAutoSlide() {
        clearInterval(autoSlideInterval);
        startAutoSlide();
    }

    // Event listeners
    const prevBtn = carousel.querySelector('.prev-btn');
    const nextBtn = carousel.querySelector('.next-btn');

    if (prevBtn) prevBtn.onclick = () => { prevImage(); resetAutoSlide(); };
    if (nextBtn) nextBtn.onclick = () => { nextImage(); resetAutoSlide(); };

    // Keyboard navigation
    carousel.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') { prevImage(); resetAutoSlide(); }
        if (e.key === 'ArrowRight') { nextImage(); resetAutoSlide(); }
    });

    // Touch/swipe support
    let startX = 0;
    let endX = 0;

    carousel.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
    });

    carousel.addEventListener('touchend', (e) => {
        endX = e.changedTouches[0].clientX;
        handleSwipe();
    });

    function handleSwipe() {
        const threshold = 50;
        const diff = startX - endX;
        
        if (Math.abs(diff) > threshold) {
            if (diff > 0) {
                nextImage();
            } else {
                prevImage();
            }
            resetAutoSlide();
        }
    }

    // Pause auto-slide on hover
    carousel.addEventListener('mouseenter', () => clearInterval(autoSlideInterval));
    carousel.addEventListener('mouseleave', startAutoSlide);

    // Initialize
    if (images.length > 0) {
        showImage(0);
        startAutoSlide();
    }
}

// Smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in animation to sections
    const sections = document.querySelectorAll('section');
    sections.forEach((section, index) => {
        section.style.animationDelay = `${index * 0.1}s`;
        section.classList.add('fade-in');
    });

    // Enhanced form interactions
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });

    // Project card hover effects
    const projectCards = document.querySelectorAll('.project-card');
    projectCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Typing effect for main title
    const title = document.querySelector('header h1');
    if (title) {
        const text = title.textContent;
        title.textContent = '';
        let i = 0;
        
        function typeWriter() {
            if (i < text.length) {
                title.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        }
        
        setTimeout(typeWriter, 500);
    }

    // Parallax effect for background
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const parallax = document.body;
        const speed = scrolled * 0.5;
        parallax.style.backgroundPosition = `center ${speed}px`;
    });

    // Status color coding
    const statusElements = document.querySelectorAll('[class*="status"]');
    statusElements.forEach(element => {
        const status = element.textContent.toLowerCase();
        if (status.includes('completed')) {
            element.classList.add('status-completed');
        } else if (status.includes('progress')) {
            element.classList.add('status-progress');
        } else if (status.includes('planned')) {
            element.classList.add('status-planned');
        }
    });
});

// Loading animation
window.addEventListener('load', function() {
    document.body.classList.add('loaded');
});

// Confirmation dialogs with custom styling
function confirmDelete(message) {
    return confirm(`⚠️ ${message}\n\nThis action cannot be undone.`);
}

// Image lazy loading
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading
document.addEventListener('DOMContentLoaded', lazyLoadImages);
