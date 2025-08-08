// Функция для установки темы
function setTheme(themeName) {
    // Сохраняем выбор пользователя в localStorage
    localStorage.setItem('theme', themeName);
    
    // Применяем тему к документу
    document.documentElement.setAttribute('data-theme', themeName);
    
    // Обновляем иконку и текст переключателя
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    
    if (themeIcon && themeText) {
        if (themeName === 'dark') {
            // Для темной темы
            themeIcon.classList.remove('bi-moon');
            themeIcon.classList.add('bi-sun');
            themeText.innerText = 'Светлая тема';
        } else {
            // Для светлой темы
            themeIcon.classList.remove('bi-sun');
            themeIcon.classList.add('bi-moon');
            themeText.innerText = 'Темная тема';
        }
    }
}

// Функция для переключения темы
function toggleTheme() {
    // Получаем текущую тему
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // Переключаем на противоположную
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    // Устанавливаем новую тему
    setTheme(newTheme);
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем предпочтения пользователя из системных настроек
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Получаем сохраненную тему или используем системную
    const savedTheme = localStorage.getItem('theme') || (prefersDarkScheme.matches ? 'dark' : 'light');
    
    // Устанавливаем начальную тему
    setTheme(savedTheme);
    
    // Добавляем обработчик для кнопки переключения темы
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Слушаем изменения системных настроек темы
    prefersDarkScheme.addEventListener('change', function(e) {
        // Если пользователь не установил тему вручную, следуем системным настройкам
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
});