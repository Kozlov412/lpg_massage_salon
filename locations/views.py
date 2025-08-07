from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Location

class LocationListView(ListView):
    """Список филиалов"""
    model = Location
    template_name = 'locations/location_list.html'
    context_object_name = 'locations'
    queryset = Location.objects.filter(is_active=True)

class LocationDetailView(DetailView):
    """Детальная информация о филиале"""
    model = Location
    template_name = 'locations/location_detail.html'
    context_object_name = 'location'