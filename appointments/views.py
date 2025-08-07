from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .models import Appointment, Review
from .forms import AppointmentForm, AppointmentStatusForm, ReviewForm
from services.models import Service
from locations.models import Location
from django.utils import timezone

class AppointmentCreateView(LoginRequiredMixin, CreateView):
    """Представление для создания новой записи на процедуру"""
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'
    success_url = reverse_lazy('appointment_list')
    
    def get_initial(self):
        """Предзаполняем форму начальными данными из GET-параметров"""
        initial = super().get_initial()
        if 'service_id' in self.request.GET:
            initial['service'] = self.request.GET.get('service_id')
        if 'location_id' in self.request.GET:
            initial['location'] = self.request.GET.get('location_id')
        return initial
    
    def get_context_data(self, **kwargs):
        """Добавляем дополнительный контекст для шаблона"""
        context = super().get_context_data(**kwargs)
        
        # Если указан ID услуги, получаем информацию о ней
        service_id = self.request.GET.get('service_id')
        if service_id:
            try:
                service = Service.objects.get(pk=service_id)
                context['selected_service'] = service
            except Service.DoesNotExist:
                pass
        
        # Если указан ID филиала, получаем информацию о нем
        location_id = self.request.GET.get('location_id')
        if location_id:
            try:
                location = Location.objects.get(pk=location_id)
                context['selected_location'] = location
            except Location.DoesNotExist:
                pass
        
        return context
    
    def form_valid(self, form):
        """Устанавливаем текущего пользователя как клиента"""
        form.instance.client = self.request.user
        messages.success(self.request, "Ваша запись успешно создана и ожидает подтверждения.")
        return super().form_valid(form)

class AppointmentListView(LoginRequiredMixin, ListView):
    """Представление для просмотра списка записей пользователя"""
    model = Appointment
    template_name = 'appointments/appointment_list.html'
    context_object_name = 'appointments'
    
    def get_queryset(self):
        # Пользователь видит только свои записи
        return Appointment.objects.filter(
            client=self.request.user
        ).order_by('-date', '-time')

class AppointmentDetailView(LoginRequiredMixin, DetailView):
    """Представление для просмотра детальной информации о записи"""
    model = Appointment
    template_name = 'appointments/appointment_detail.html'
    context_object_name = 'appointment'
    
    def get_queryset(self):
        # Пользователь может просматривать только свои записи
        return Appointment.objects.filter(client=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Проверяем, оставил ли пользователь отзыв
        context['has_review'] = hasattr(self.object, 'review')
        return context

class AppointmentCancelView(LoginRequiredMixin, UpdateView):
    """Представление для отмены записи"""
    model = Appointment
    template_name = 'appointments/appointment_cancel.html'
    fields = []  # Пустой список, так как мы не редактируем поля через форму
    success_url = reverse_lazy('appointment_list')
    
    def get_queryset(self):
        # Пользователь может отменять только свои записи
        return Appointment.objects.filter(client=self.request.user)
    
    def form_valid(self, form):
        # Изменяем статус на "отменена"
        self.object = form.save(commit=False)
        self.object.status = 'canceled'
        self.object.save()
        messages.success(self.request, "Запись успешно отменена.")
        return redirect(self.get_success_url())

class ReviewCreateView(LoginRequiredMixin, CreateView):
    """Представление для создания отзыва о процедуре"""
    model = Review
    form_class = ReviewForm
    template_name = 'appointments/review_form.html'
    
    def get_appointment(self):
        """Получение заявки, для которой создается отзыв"""
        return get_object_or_404(
            Appointment,
            pk=self.kwargs['appointment_id'],
            client=self.request.user,
            status='completed'
        )
    
    def get_context_data(self, **kwargs):
        """Добавляем информацию о заявке в контекст"""
        context = super().get_context_data(**kwargs)
        context['appointment'] = self.get_appointment()
        return context
    
    def form_valid(self, form):
        """Привязываем отзыв к заявке"""
        form.instance.appointment = self.get_appointment()
        messages.success(self.request, "Ваш отзыв успешно отправлен. Спасибо за ваше мнение!")
        return super().form_valid(form)
    
    def get_success_url(self):
        """Перенаправление после успешного создания отзыва"""
        return reverse('appointment_detail', kwargs={'pk': self.kwargs['appointment_id']})

# Представления для администраторов
class StaffRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь является сотрудником"""
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, "У вас нет доступа к этой странице. Необходимы права администратора.")
        return redirect('home')

class AdminAppointmentListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """Представление для просмотра всех заявок администратором"""
    model = Appointment
    template_name = 'appointments/admin_appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset().order_by('-date', '-time')
        
        # Фильтрация по статусу
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Фильтрация по филиалу
        location_id = self.request.GET.get('location')
        if location_id:
            queryset = queryset.filter(location_id=location_id)
            
        # Фильтрация по дате
        date = self.request.GET.get('date')
        if date:
            queryset = queryset.filter(date=date)
            
        # Поиск по клиенту
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                client__username__icontains=search_query) | queryset.filter(
                client__first_name__icontains=search_query) | queryset.filter(
                client__last_name__icontains=search_query) | queryset.filter(
                client__email__icontains=search_query
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locations'] = Location.objects.filter(is_active=True)
        context['status_choices'] = Appointment.STATUS_CHOICES
        
        # Текущие фильтры
        context['current_status'] = self.request.GET.get('status', '')
        context['current_location'] = self.request.GET.get('location', '')
        context['current_date'] = self.request.GET.get('date', '')
        context['current_search'] = self.request.GET.get('search', '')
        
        return context

class AdminAppointmentDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    """Представление для просмотра детальной информации о заявке администратором"""
    model = Appointment
    template_name = 'appointments/admin_appointment_detail.html'
    context_object_name = 'appointment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_form'] = AppointmentStatusForm(instance=self.object)
        # Проверяем, есть ли у заявки отзыв
        try:
            context['review'] = self.object.review
        except Review.DoesNotExist:
            context['review'] = None
        
        return context

class AdminAppointmentUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """Представление для обновления статуса заявки администратором"""
    model = Appointment
    form_class = AppointmentStatusForm
    template_name = 'appointments/admin_appointment_update.html'
    
    def get_success_url(self):
        return reverse('admin_appointment_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Статус заявки успешно обновлен на '{self.object.get_status_display()}'.")
        
        # Если отметили как уведомленный
        if 'notified' in form.changed_data and self.object.notified:
            # Здесь можно добавить логику отправки уведомлений клиенту
            pass
        
        return response

class AdminReviewListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """Представление для просмотра всех отзывов администратором"""
    model = Review
    template_name = 'appointments/admin_review_list.html'
    context_object_name = 'reviews'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created')
        
        # Фильтрация по публикации
        is_published = self.request.GET.get('is_published')
        if is_published:
            queryset = queryset.filter(is_published=is_published == 'true')
            
        # Фильтрация по рейтингу
        rating = self.request.GET.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)
            
        # Фильтрация по филиалу
        location_id = self.request.GET.get('location')
        if location_id:
            queryset = queryset.filter(appointment__location_id=location_id)
            
        # Поиск
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(comment__icontains=search_query) | queryset.filter(
                appointment__client__username__icontains=search_query) | queryset.filter(
                appointment__client__first_name__icontains=search_query) | queryset.filter(
                appointment__client__last_name__icontains=search_query
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locations'] = Location.objects.all()
        
        # Текущие фильтры
        context['current_published'] = self.request.GET.get('is_published', '')
        context['current_rating'] = self.request.GET.get('rating', '')
        context['current_location'] = self.request.GET.get('location', '')
        context['current_search'] = self.request.GET.get('search', '')
        
        return context

class AdminReviewDetailView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """Представление для обновления статуса публикации отзыва администратором"""
    model = Review
    template_name = 'appointments/admin_review_detail.html'
    context_object_name = 'review'
    fields = ['is_published']
    
    def get_success_url(self):
        return reverse('admin_review_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.object.is_published:
            messages.success(self.request, "Отзыв успешно опубликован.")
        else:
            messages.success(self.request, "Отзыв снят с публикации.")
        return response  