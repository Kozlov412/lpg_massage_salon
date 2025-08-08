document.addEventListener('DOMContentLoaded', function() {
    const dateInput = document.getElementById('id_date');
    const timeInput = document.getElementById('id_time');
    
    if (!dateInput || !timeInput) {
        return; // Выходим, если элементы не найдены
    }
    
    // Рабочие часы по дням недели (0 = воскресенье, 1 = понедельник, ..., 6 = суббота)
    const workingHours = {
        1: { start: '10:00', end: '22:00' }, // Понедельник
        2: { start: '10:00', end: '22:00' }, // Вторник
        3: { start: '10:00', end: '22:00' }, // Среда
        4: { start: '10:00', end: '22:00' }, // Четверг
        5: { start: '10:00', end: '22:00' }, // Пятница
        6: { start: '10:00', end: '20:00' }, // Суббота
        0: { start: '10:00', end: '20:00' }  // Воскресенье
    };
    
    // Функция получения названия дня недели
    function getDayName(dayOfWeek) {
        const days = [
            'воскресенье', 'понедельник', 'вторник', 
            'среду', 'четверг', 'пятницу', 'субботу'
        ];
        return days[dayOfWeek];
    }
    
    // Функция обновления доступных часов
    function updateAvailableHours() {
        if (!dateInput.value) return;
        
        const selectedDate = new Date(dateInput.value);
        const dayOfWeek = selectedDate.getDay(); // 0-6 (Вс-Сб)
        
        // Получаем рабочие часы для выбранного дня
        const hours = workingHours[dayOfWeek];
        
        // Устанавливаем минимальное и максимальное время
        timeInput.setAttribute('min', hours.start);
        timeInput.setAttribute('max', hours.end);
        
        // Проверяем, что выбранное время находится в пределах рабочих часов
        if (timeInput.value) {
            if (timeInput.value < hours.start) {
                timeInput.value = hours.start;
            }
            if (timeInput.value > hours.end) {
                timeInput.value = hours.end;
            }
        }
        
        // Добавляем подсказку под полем времени
        let timeHelp = document.getElementById('time-help');
        if (!timeHelp) {
            timeHelp = document.createElement('small');
            timeHelp.id = 'time-help';
            timeHelp.className = 'form-text text-muted mt-1';
            timeInput.parentNode.appendChild(timeHelp);
        }
        timeHelp.textContent = `Рабочие часы в ${getDayName(dayOfWeek)}: ${hours.start} - ${hours.end}`;
    }
    
    // Устанавливаем сегодняшнюю дату как минимальную
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const todayFormatted = `${year}-${month}-${day}`;
    dateInput.setAttribute('min', todayFormatted);
    
    // Добавляем обработчики событий
    dateInput.addEventListener('change', updateAvailableHours);
    timeInput.addEventListener('focus', updateAvailableHours);
    
    // Если дата уже выбрана, обновляем доступные часы
    if (dateInput.value) {
        updateAvailableHours();
    }
    
    // Дополнительная проверка перед отправкой формы
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (dateInput.value && timeInput.value) {
                const selectedDate = new Date(dateInput.value);
                const dayOfWeek = selectedDate.getDay();
                const hours = workingHours[dayOfWeek];
                
                if (timeInput.value < hours.start || timeInput.value > hours.end) {
                    e.preventDefault();
                    alert(`Пожалуйста, выберите время в рабочие часы: ${hours.start} - ${hours.end}`);
                }
            }
        });
    }
});