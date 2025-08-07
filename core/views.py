from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from services.models import ServiceCategory, Service
from locations.models import Location
from appointments.models import Appointment
from .models import Client
from .forms import UserProfileForm, ClientProfileForm

class HomeView(TemplateView):
    """Главная страница сайта"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ServiceCategory.objects.all()[:4]  # Первые 4 категории для главной
        context['services'] = Service.objects.filter(is_active=True)[:6]  # Первые 6 активных услуг
        context['locations'] = Location.objects.filter(is_active=True)  # Все активные филиалы
        return context
    
class AboutView(TemplateView):
    """Страница о салоне"""
    template_name = 'core/about.html'
    
class ContactView(TemplateView):
    """Страница контактов"""
    template_name = 'core/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locations'] = Location.objects.filter(is_active=True)
        return context

class ProfileView(LoginRequiredMixin, TemplateView):
    """Страница личного кабинета"""
    template_name = 'core/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем историю записей пользователя
        context['appointments'] = Appointment.objects.filter(
            client=self.request.user
        ).order_by('-date', '-time')[:5]  # Последние 5 записей
        
        # Проверяем, есть ли профиль клиента, или создаем новый
        client, created = Client.objects.get_or_create(user=self.request.user)
        
        context['client'] = client
        return context

class ProfileEditView(LoginRequiredMixin, TemplateView):
    """Редактирование профиля"""
    template_name = 'core/profile_edit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user = self.request.user
        client, created = Client.objects.get_or_create(user=user)
        
        if self.request.method == 'POST':
            user_form = UserProfileForm(self.request.POST, instance=user)
            client_form = ClientProfileForm(self.request.POST, instance=client)
        else:
            user_form = UserProfileForm(instance=user)
            client_form = ClientProfileForm(instance=client)
            
        context['user_form'] = user_form
        context['client_form'] = client_form
        return context
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        user_form = context['user_form']
        client_form = context['client_form']
        
        if user_form.is_valid() and client_form.is_valid():
            user_form.save()
            client_form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
        
        return self.render_to_response(context)