from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm

from Univrequest.models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'matricule', 'faculte', 'departement', 'filiere', 'niveau',
        )

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'  # ou listez les champs manuellement si vous préférez