from django import forms
from .models import Appointment, Review

class AppointmentForm(forms.ModelForm):
    """Форма для создания записи"""
    class Meta:
        model = Appointment
        fields = ['service', 'location', 'date', 'time', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Оставьте комментарий при необходимости'}),
        }

class AppointmentStatusForm(forms.ModelForm):
    """Форма для обновления статуса заявки администратором"""
    class Meta:
        model = Appointment
        fields = ['status', 'admin_notes', 'notified']
        widgets = {
            'admin_notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Заметки для администраторов'}),
        }

class ReviewForm(forms.ModelForm):
    """Форма для создания отзыва о процедуре"""
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Оставьте свой отзыв о процедуре'}),
        }