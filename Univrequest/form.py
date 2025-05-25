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
    def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)

        # Style de base
          base_classes = 'w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-orange-500'

        # Style spécial pour les champs select
          for field_name, field in self.fields.items():
            widget = field.widget

            # Champs sélectionnés dynamiquement (ForeignKey → Select)
            if isinstance(widget, forms.Select):
                widget.attrs.update({
                    'class': base_classes + ' bg-white text-gray-700',
                })

            # Champs texte normaux
            elif isinstance(widget, (forms.TextInput, forms.EmailInput, forms.PasswordInput)):
                widget.attrs.update({
                    'class': base_classes,
                    'placeholder': field.label
                })

            # Champs zone de texte (si tu en ajoutes plus tard)
            elif isinstance(widget, forms.Textarea):
                widget.attrs.update({
                    'class': base_classes + ' h-32 resize-none',
                    'placeholder': field.label
                })

            # Par défaut, applique style de base
            else:
                widget.attrs.update({
                    'class': base_classes
                })

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'  # ou listez les champs manuellement si vous préférez