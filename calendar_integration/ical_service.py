from icalendar import Calendar, Event, vCalAddress, vText
import datetime
import pytz
from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_bytes

def generate_ical_for_appointment(appointment, site_url):
    """
    Генерация iCalendar файла для записи
    """
    # Создание календаря
    cal = Calendar()
    cal.add('prodid', '-//LPG Massage Salon//yuanna.ru//')
    cal.add('version', '2.0')
    
    # Создание события
    event = Event()
    
    # Базовая информация о событии
    start_time = datetime.datetime.combine(appointment.date, appointment.time)
    tz = pytz.timezone('Europe/Moscow')  # Используйте соответствующий часовой пояс
    start_time = tz.localize(start_time)
    
    # Длительность процедуры
    end_time = start_time + appointment.service.duration
    
    # Добавляем информацию о событии
    event.add('summary', f"LPG Массаж: {appointment.service.name}")
    event.add('dtstart', start_time)
    event.add('dtend', end_time)
    event.add('dtstamp', datetime.datetime.now(tz=tz))
    event.add('location', appointment.location.address)
    
    # Описание события
    description = f"""
    Услуга: {appointment.service.name}
    Салон: {appointment.location.name}
    Адрес: {appointment.location.address}
    Телефон: {appointment.location.phone}
    
    Дополнительная информация:
    {appointment.notes}
    
    Статус: {appointment.get_status_display()}
    """
    event.add('description', description)
    
    # Уникальный идентификатор события
    event['uid'] = f"appointment-{appointment.id}@yuanna.ru"
    
    # Добавляем организатора
    organizer = vCalAddress('MAILTO:info@yuanna.ru')
    organizer.params['cn'] = vText('ЮАнна студия массажа')
    event['organizer'] = organizer
    
    # URL для просмотра детальной информации о записи
    event.add('url', f"{site_url}{reverse('appointment_detail', kwargs={'pk': appointment.id})}")
    
    # Добавляем событие в календарь
    cal.add_component(event)
    
    # Возвращаем содержимое календаря в формате iCalendar
    return cal.to_ical()