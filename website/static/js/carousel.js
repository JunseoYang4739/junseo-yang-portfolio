function initCarousel(carouselId) {
    const carousel = document.getElementById(carouselId);
    const images = carousel.querySelectorAll('.carousel-images');
    let currentIndex = 0;

    function showImage(index) {
        images.forEach(img => img.classList.remove('active'));
        images[index].classList.add('active');
    }

    function nextImage() {
        currentIndex = (currentIndex + 1) % images.length;
        showImage(currentIndex);
    }

    function prevImage() {
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        showImage(currentIndex);
    }

    const prevBtn = carousel.querySelector('.prev-btn');
    const nextBtn = carousel.querySelector('.next-btn');

    if (prevBtn) prevBtn.onclick = prevImage;
    if (nextBtn) nextBtn.onclick = nextImage;

    if (images.length > 0) {
        showImage(0);
    }
}
