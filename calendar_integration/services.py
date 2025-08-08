import os
import datetime
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.conf import settings
from .models import GoogleCalendarCredentials

# Настройки Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

def get_google_calendar_service(user):
    """
    Получение сервиса Google Calendar для пользователя
    """
    # Проверка наличия учетных данных пользователя
    try:
        credentials_obj = GoogleCalendarCredentials.objects.get(user=user)
        credentials_json = credentials_obj.token
        
        # Создание объекта учетных данных
        credentials = Credentials(
            token=credentials_json.get('token'),
            refresh_token=credentials_json.get('refresh_token'),
            token_uri=credentials_json.get('token_uri'),
            client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
            client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
            scopes=SCOPES
        )
        
        # Проверка действительности учетных данных
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            
            # Обновляем токен в базе данных
            credentials_obj.token = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            credentials_obj.save()
        
        # Создание сервиса
        service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
        return service
    
    except GoogleCalendarCredentials.DoesNotExist:
        return None

def add_appointment_to_google_calendar(user, appointment):
    """
    Добавление записи в Google Calendar
    """
    service = get_google_calendar_service(user)
    if not service:
        return None
    
    # Создание начальной и конечной даты/времени события
    start_time = datetime.datetime.combine(appointment.date, appointment.time)
    # Предполагаем, что у нас есть длительность процедуры в объекте appointment.service.duration
    # duration может быть timedelta, поэтому можно просто прибавить его к start_time
    end_time = start_time + appointment.service.duration
    
    # Создание события в формате Google Calendar
    event = {
        'summary': f"LPG Массаж: {appointment.service.name}",
        'location': appointment.location.address,
        'description': f"""
        Услуга: {appointment.service.name}
        Салон: {appointment.location.name}
        Адрес: {appointment.location.address}
        Телефон: {appointment.location.phone}
        
        Дополнительная информация:
        {appointment.notes}
        """,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Europe/Moscow',  # Используйте соответствующий часовой пояс
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Europe/Moscow',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},  # За день до события
                {'method': 'popup', 'minutes': user.calendar_settings.reminder_time},  # По настройке пользователя
            ],
        },
    }
    
    # Добавление события в календарь
    event = service.events().insert(calendarId='primary', body=event).execute()
    
    # Возвращаем ID события для сохранения в базе данных
    return event.get('id')

def update_appointment_in_google_calendar(user, appointment, event_id):
    """
    Обновление существующего события в Google Calendar
    """
    service = get_google_calendar_service(user)
    if not service:
        return False
    
    # Аналогично add_appointment_to_google_calendar
    start_time = datetime.datetime.combine(appointment.date, appointment.time)
    end_time = start_time + appointment.service.duration
    
    # Получение текущего события
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    
    # Обновление данных события
    event['summary'] = f"LPG Массаж: {appointment.service.name}"
    event['location'] = appointment.location.address
    event['description'] = f"""
    Услуга: {appointment.service.name}
    Салон: {appointment.location.name}
    Адрес: {appointment.location.address}
    Телефон: {appointment.location.phone}
    
    Дополнительная информация:
    {appointment.notes}
    """
    event['start'] = {
        'dateTime': start_time.isoformat(),
        'timeZone': 'Europe/Moscow',
    }
    event['end'] = {
        'dateTime': end_time.isoformat(),
        'timeZone': 'Europe/Moscow',
    }
    
    # Обновление события в календаре
    updated_event = service.events().update(
        calendarId='primary', eventId=event_id, body=event
    ).execute()
    
    return updated_event.get('id') == event_id

def remove_appointment_from_google_calendar(user, event_id):
    """
    Удаление события из Google Calendar
    """
    service = get_google_calendar_service(user)
    if not service:
        return False
    
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return True
    except Exception as e:
        print(f"Ошибка при удалении события из календаря: {e}")
        return False