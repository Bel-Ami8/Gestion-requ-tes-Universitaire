from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .form import CustomUserChangeForm, CustomUserCreationForm
from .models import User, Departement, Faculte, Filiere
# Register your models here.

class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_etudiant', 'is_receptionniste','is_reception_departement','is_fac_gestionnaire')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'matricule', 'faculte', 'departement', 'filiere', 'niveau')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Rôles', {'fields': ('is_etudiant', 'is_receptionniste', 'is_reception_departement', 'is_fac_gestionnaire')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','first_name', 'last_name', 'email', 'matricule', 'faculte', 'departement', 'filiere', 'niveau', 'password1', 'password2', 'is_etudiant', 'is_receptionniste', 'is_reception_departement', 'is_fac_gestionnaire'),
        }),
    )
    search_fields = ('username', 'email', 'matricule')

admin.site.register(User,UserAdmin)
admin.site.register(Faculte)
admin.site.register(Departement)
admin.site.register(Filiere)