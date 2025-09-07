from django.shortcuts import render
from django.views.generic import ListView
from .models import BeforeAfterResult
from services.models import ServiceCategory

class ResultsListView(ListView):
    model = BeforeAfterResult
    template_name = 'results/results_list.html'
    context_object_name = 'results'
    
    def get_queryset(self):
        # Получаем только опубликованные результаты
        return BeforeAfterResult.objects.filter(is_published=True).select_related('service')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Группируем результаты по категориям услуг
        categories = ServiceCategory.objects.all()
        grouped_results = {}
        
        for category in categories:
            # Получаем все результаты для услуг этой категории
            category_results = self.get_queryset().filter(service__category=category)
            if category_results.exists():
                grouped_results[category] = category_results
        
        context['grouped_results'] = grouped_results
        return context


