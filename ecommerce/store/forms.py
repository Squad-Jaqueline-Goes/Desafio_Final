# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Address

class CustomUserCreationForm(UserCreationForm):
    street = forms.CharField(max_length=255, required=True, label="Rua")
    city = forms.CharField(max_length=100, required=True, label="Cidade")
    state = forms.CharField(max_length=100, required=True, label="Estado")
    zipcode = forms.CharField(max_length=20, required=True, label="CEP")
    country = forms.CharField(max_length=100, initial="Brasil", label="País")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'street', 'city', 'state', 'zipcode', 'country']
