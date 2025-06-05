from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm

from Univrequest.models import Documents, Requetes, TypeRequetes, User,Message


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


class MessageForm(forms.ModelForm):
    fichiers_upload = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control-file'}),  # Ici on utilise FileInput au lieu de ClearableFileInput
        required=False,
        label="Pièces jointes"
    )

    class Meta:
        model = Message
        fields = ['sujet', 'contenu', 'fichiers']

        widgets = {
            'destinataire': forms.Select(attrs={'class': 'form-select'}),
            'sujet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sujet'}),
            'contenu': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Écris ton message ici...'}),
        }


class ReceptionnisteUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'matricule', 'faculte', 'departement', 'filiere', 'niveau',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_classes = 'w-full border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-orange-500'

        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.Select):
                widget.attrs.update({
                    'class': base_classes + ' bg-white text-gray-700',
                })
            elif isinstance(widget, (forms.TextInput, forms.EmailInput, forms.PasswordInput)):
                widget.attrs.update({
                    'class': base_classes,
                    'placeholder': field.label
                })
            elif isinstance(widget, forms.Textarea):
                widget.attrs.update({
                    'class': base_classes + ' h-32 resize-none',
                    'placeholder': field.label
                })
            else:
                widget.attrs.update({
                    'class': base_classes
                })


class RequeteReceptionnisteForm(forms.ModelForm):
    class Meta:
        model = Requetes
        fields = ('statut', 'priorite', 'documents', 'descrition')
        widgets = {
            'statut': forms.Select(attrs={'class': 'border rounded p-2'}),
            'note_traitement': forms.Textarea(attrs={
                'class': 'border rounded p-2',
                'rows': 4,
                'placeholder': 'Ajouter une note…'
            }),
        }


class RequeteForm(forms.ModelForm):
    class Meta:
        model = Requetes
        exclude = ['utilisateur', 'documents', 'date_creation', 'date_suppression', 'statut']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Force l’affichage de tous les types de requêtes
        self.fields['type_requete'].queryset = TypeRequetes.objects.all()
        self.fields['type_requete'].empty_label = "Sélectionnez un type"