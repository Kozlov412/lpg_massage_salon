from locations.models import Location

def locations_processor(request):
    """Добавляет список активных филиалов во все шаблоны"""
    return {
        'locations': Location.objects.filter(is_active=True)
    }