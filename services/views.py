from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import ServiceCategory, Service, ServiceReview
from .forms import ServiceReviewForm
from locations.models import Location

class ServiceCategoryListView(ListView):
    """Список всех категорий услуг"""
    model = ServiceCategory
    template_name = 'services/category_list.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_services'] = Service.objects.filter(is_active=True).order_by('category', 'name')
        return context

class ServiceListView(ListView):
    """Список услуг в конкретной категории"""
    model = Service
    template_name = 'services/service_list.html'
    context_object_name = 'services'
    
    def get_queryset(self):
        self.category = get_object_or_404(ServiceCategory, pk=self.kwargs['category_id'])
        return Service.objects.filter(category=self.category, is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

class ServiceDetailView(DetailView):
    """Детальная информация об услуге"""
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем другие услуги из той же категории (не более 3)
        context['related_services'] = Service.objects.filter(
            category=self.object.category, 
            is_active=True
        ).exclude(
            pk=self.object.pk
        ).order_by('?')[:3]
        
        # Получаем только опубликованные отзывы
        context['reviews'] = ServiceReview.objects.filter(
            service=self.object,
            is_published=True
        ).order_by('-created')[:5]
        
        # Средний рейтинг
        reviews = ServiceReview.objects.filter(service=self.object, is_published=True)
        if reviews.exists():
            avg_rating = sum(review.rating for review in reviews) / len(reviews)
            context['avg_rating'] = avg_rating
            context['review_count'] = len(reviews)
        
        # Проверяем, может ли пользователь оставить отзыв
        if self.request.user.is_authenticated:
            # Отображаем форму для создания отзыва
            context['review_form'] = ServiceReviewForm()
            
            # Проверяем, оставил ли пользователь уже отзыв
            context['user_reviewed'] = ServiceReview.objects.filter(
                service=self.object, 
                user=self.request.user
            ).exists()
        
        # Добавляем список филиалов для формы отзыва
        context['locations'] = Location.objects.filter(is_active=True)
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Обработка отправки формы отзыва"""
        if not request.user.is_authenticated:
            messages.error(request, "Для отправки отзыва необходимо авторизоваться.")
            return redirect('account_login')
            
        self.object = self.get_object()
        form = ServiceReviewForm(request.POST)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.service = self.object
            
            # Проверка на дубликат отзыва
            if ServiceReview.objects.filter(service=self.object, user=request.user).exists():
                messages.error(request, "Вы уже оставляли отзыв на эту услугу.")
            else:
                review.save()
                messages.success(request, "Спасибо за ваш отзыв! После модерации он будет опубликован.")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
        
        return redirect('service_detail', pk=self.object.pk)