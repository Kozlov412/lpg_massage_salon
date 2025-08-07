from django import forms
from .models import ServiceReview

class ServiceReviewForm(forms.ModelForm):
    """Форма для создания отзыва об услуге"""
    class Meta:
        model = ServiceReview
        fields = ['rating', 'comment', 'location']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Поделитесь своим мнением об услуге'}),
        }