// Ждем, пока документ будет полностью загружен
document.addEventListener('DOMContentLoaded', function() {
    
    // Плавная прокрутка для всех якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#' || !targetId) return;
            
            const targetEl = document.querySelector(targetId);
            if (!targetEl) return;
            
            window.scrollTo({
                top: targetEl.offsetTop - 80,
                behavior: 'smooth'
            });
        });
    });
    
    // Добавление анимации для карточек при прокрутке
    const cards = document.querySelectorAll('.card');
    
    function checkVisibility() {
        cards.forEach(card => {
            const rect = card.getBoundingClientRect();
            const isVisible = (rect.top <= window.innerHeight * 0.8) && (rect.bottom >= 0);
            
            if (isVisible) {
                card.classList.add('fade-in');
            }
        });
    }
    
    // Запускаем проверку видимости при загрузке и скролле
    checkVisibility();
    window.addEventListener('scroll', checkVisibility);
    
    // Анимация чисел для статистики (если есть на странице)
    const stats = document.querySelectorAll('.counter');
    let counted = false;
    
    function animateNumbers() {
        if (stats.length > 0 && !counted) {
            const statSection = document.querySelector('.stats-section');
            if (!statSection) return;
            
            const rect = statSection.getBoundingClientRect();
            const isVisible = (rect.top <= window.innerHeight * 0.8) && (rect.bottom >= 0);
            
            if (isVisible) {
                stats.forEach(stat => {
                    const targetValue = parseInt(stat.getAttribute('data-target'));
                    let count = 0;
                    const duration = 2000; // 2 секунды
                    const interval = Math.floor(duration / targetValue);
                    
                    let counter = setInterval(() => {
                        count++;
                        stat.innerText = count;
                        
                        if (count >= targetValue) {
                            clearInterval(counter);
                        }
                    }, Math.max(interval, 10));
                });
                
                counted = true;
            }
        }
    }
    
    // Запускаем анимацию чисел при скролле
    window.addEventListener('scroll', animateNumbers);
});