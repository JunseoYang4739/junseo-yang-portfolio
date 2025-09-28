function initCarousel(carouselId) {
    const carousel = document.getElementById(carouselId);
    if (!carousel) return;
    
    const images = carousel.querySelectorAll('.carousel-images');
    if (images.length <= 1) return;
    
    let currentIndex = 0;
    
    // Create dots
    const dotsContainer = carousel.querySelector('.carousel-dots');
    dotsContainer.innerHTML = '';
    for (let i = 0; i < images.length; i++) {
        const dot = document.createElement('span');
        dot.className = 'carousel-dot';
        if (i === 0) dot.classList.add('active');
        dot.addEventListener('click', () => goToSlide(i));
        dotsContainer.appendChild(dot);
    }
    
    function showSlide(index) {
        // Hide all images
        images.forEach(img => {
            img.style.display = 'none';
            img.classList.remove('slide-in');
        });
        
        // Show current image with animation
        images[index].style.display = 'block';
        setTimeout(() => {
            images[index].classList.add('slide-in');
        }, 10);
        
        // Update dots
        const dots = dotsContainer.querySelectorAll('.carousel-dot');
        dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === index);
        });
        
        currentIndex = index;
    }
    
    function goToSlide(index) {
        showSlide(index);
    }
    
    // Arrow click handlers
    const prevArrow = carousel.querySelector('.carousel-arrow.prev');
    const nextArrow = carousel.querySelector('.carousel-arrow.next');
    
    if (prevArrow) {
        prevArrow.addEventListener('click', () => {
            currentIndex = currentIndex === 0 ? images.length - 1 : currentIndex - 1;
            showSlide(currentIndex);
        });
    }
    
    if (nextArrow) {
        nextArrow.addEventListener('click', () => {
            currentIndex = currentIndex === images.length - 1 ? 0 : currentIndex + 1;
            showSlide(currentIndex);
        });
    }
    
    // Initialize first slide
    showSlide(0);
}

// Global function for onclick handlers
function changeSlide(carouselId, direction) {
    const carousel = document.getElementById(carouselId);
    if (!carousel) return;
    
    const images = carousel.querySelectorAll('.carousel-images');
    let currentIndex = 0;
    
    // Find current active image
    images.forEach((img, i) => {
        if (img.style.display === 'block') {
            currentIndex = i;
        }
    });
    
    // Calculate new index
    let newIndex = currentIndex + direction;
    if (newIndex >= images.length) newIndex = 0;
    if (newIndex < 0) newIndex = images.length - 1;
    
    // Hide all images
    images.forEach(img => {
        img.style.display = 'none';
        img.classList.remove('slide-in');
    });
    
    // Show new image with animation
    images[newIndex].style.display = 'block';
    setTimeout(() => {
        images[newIndex].classList.add('slide-in');
    }, 10);
    
    // Update dots
    const dots = carousel.querySelectorAll('.carousel-dot');
    dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === newIndex);
    });
}
