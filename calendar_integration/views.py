from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.conf import settings
from google_auth_oauthlib.flow import Flow
from .models import GoogleCalendarCredentials, CalendarSettings
from .services import add_appointment_to_google_calendar, update_appointment_in_google_calendar, remove_appointment_from_google_calendar
from .ical_service import generate_ical_for_appointment
from appointments.models import Appointment

@login_required
def calendar_settings_view(request):
    """
    Представление для настройки интеграции с календарями
    """
    # Получаем или создаем настройки календаря для пользователя
    settings, created = CalendarSettings.objects.get_or_create(user=request.user)
    
    # Проверяем, есть ли у пользователя учетные данные Google Calendar
    has_google_auth = hasattr(request.user, 'google_calendar')
    
    if request.method == 'POST':
        # Обработка формы настроек
        calendar_type = request.POST.get('calendar_type')
        add_appointments = 'add_appointments' in request.POST
        update_appointments = 'update_appointments' in request.POST
        remove_canceled = 'remove_canceled' in request.POST
        reminder_time = int(request.POST.get('reminder_time', 60))
        
        # Обновляем настройки
        settings.calendar_type = calendar_type
        settings.add_appointments = add_appointments
        settings.update_appointments = update_appointments
        settings.remove_canceled = remove_canceled
        settings.reminder_time = reminder_time
        settings.save()
        
        messages.success(request, "Настройки календаря успешно сохранены.")
        return redirect('calendar_settings')
    
    return render(request, 'calendar_integration/settings.html', {
        'settings': settings,
        'has_google_auth': has_google_auth,
    })

@login_required
def google_auth_init(request):
    """
    Начало процесса авторизации Google Calendar
    """
    # Создаем URL для перенаправления после авторизации
    redirect_uri = request.build_absolute_uri(reverse('google_auth_callback'))
    
    # Создаем объект Flow для авторизации
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri],
            }
        },
        scopes=['https://www.googleapis.com/auth/calendar'],
    )
    
    # Задаем URL для перенаправления
    flow.redirect_uri = redirect_uri
    
    # Генерируем URL для авторизации
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
    )
    
    # Сохраняем состояние в сессии
    request.session['google_auth_state'] = state
    
    # Перенаправляем пользователя на URL авторизации
    return redirect(authorization_url)

@login_required
def google_auth_callback(request):
    """
    Обработка ответа от Google после авторизации
    """
    # Получаем состояние из сессии
    state = request.session.get('google_auth_state')
    
    # Создаем объект Flow для получения токена
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [request.build_absolute_uri(reverse('google_auth_callback'))],
            }
        },
        scopes=['https://www.googleapis.com/auth/calendar'],
        state=state,
    )
    
    # Задаем URL для перенаправления
    flow.redirect_uri = request.build_absolute_uri(reverse('google_auth_callback'))
    
    # Обмен кода авторизации на токен
    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)
    
    # Получаем учетные данные
    credentials = flow.credentials
    
    # Сохраняем учетные данные в базе данных
    credentials_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
    }
    
    # Обновляем или создаем запись в базе данных
    GoogleCalendarCredentials.objects.update_or_create(
        user=request.user,
        defaults={'token': credentials_data}
    )
    
    messages.success(request, "Авторизация Google Calendar успешно выполнена.")
    return redirect('calendar_settings')

@login_required
def remove_google_auth(request):
    """
    Удаление авторизации Google Calendar
    """
    if request.method == 'POST':
        # Удаляем учетные данные из базы данных
        GoogleCalendarCredentials.objects.filter(user=request.user).delete()
        
        # Обновляем настройки календаря
        if hasattr(request.user, 'calendar_settings'):
            if request.user.calendar_settings.calendar_type == 'google':
                request.user.calendar_settings.calendar_type = 'none'
                request.user.calendar_settings.save()
        
        messages.success(request, "Авторизация Google Calendar успешно удалена.")
    
    return redirect('calendar_settings')

@login_required
def download_ical(request, appointment_id):
    """
    Скачивание iCalendar файла для записи
    """
    # Получаем запись
    appointment = get_object_or_404(Appointment, id=appointment_id, client=request.user)
    
    # Генерируем iCalendar файл
    site_url = request.build_absolute_uri('/').rstrip('/')
    ical_data = generate_ical_for_appointment(appointment, site_url)
    
    # Отправляем файл пользователю
    response = HttpResponse(ical_data, content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="appointment-{appointment.id}.ics"'
    
    return response