# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    street = forms.CharField(
        max_length=255,
        required=True,
        label="Rua",
        widget=forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Digite sua rua'})
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        label="Cidade",
        widget=forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Digite sua cidade'})
    )
    state = forms.CharField(
        max_length=100,
        required=True,
        label="Estado",
        widget=forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Digite seu estado'})
    )
    zipcode = forms.CharField(
        max_length=20,
        required=True,
        label="CEP",
        widget=forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Digite seu CEP'})
    )
    country = forms.CharField(
        max_length=100,
        initial="Brasil",
        label="País",
        widget=forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Digite seu país'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'street', 'city', 'state', 'zipcode', 'country']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Digite seu nome de usuário'}),
            'email': forms.EmailInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Digite seu email'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Digite sua senha'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Confirme sua senha'}),
        }
