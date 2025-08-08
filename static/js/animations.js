// Функция для анимации элементов при прокрутке
function animateOnScroll() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;
        
        if (elementPosition < windowHeight - 50) {
            element.classList.add('animate-visible');
        }
    });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Первичный запуск для элементов в видимой области
    animateOnScroll();
    
    // Добавление обработчика прокрутки
    window.addEventListener('scroll', animateOnScroll);
});