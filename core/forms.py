from django import forms
from django.contrib.auth.models import User
from .models import Client

class UserProfileForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""
    first_name = forms.CharField(
        max_length=30, 
        label="Имя", 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30, 
        label="Фамилия", 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Email", 
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ClientProfileForm(forms.ModelForm):
    """Форма для дополнительных данных клиента"""
    phone = forms.CharField(
        max_length=20,
        label="Номер телефона",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (___) ___-__-__'
        })
    )

    class Meta:
        model = Client
        fields = ['phone']
        labels = {
            'phone': 'Телефон'
        }