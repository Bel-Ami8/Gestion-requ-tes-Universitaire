from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .form import CustomUserChangeForm, CustomUserCreationForm
from .models import User, Departement, Faculte, Filiere,Requetes,RequeteRapport , Message ,Notification,TypeRequetes, Documents, Rapport,MiseAJourRequete
# Register your models here.

class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_etudiant', 'is_receptionniste')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'matricule', 'faculte', 'departement', 'filiere', 'niveau')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Rôles', {'fields': ('is_etudiant', 'is_receptionniste')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','first_name', 'last_name', 'email', 'matricule', 'faculte', 'departement', 'filiere', 'niveau', 'password1', 'password2', 'is_etudiant', 'is_receptionniste'),
        }),
    )
    search_fields = ('username', 'email', 'matricule')


class TypeRequetesAdmin(admin.ModelAdmin):
    list_display = ('id', 'libelle')
    search_fields = ('libelle',)


class DocumentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom_fichier', 'chemin_fichier', 'type_fichier', 'taille', 'date_ajout', 'requete')
    search_fields = ('nom_fichier', 'type_fichier')
    list_filter = ('type_fichier', 'date_ajout')


class RapportAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_traitement', 'résultat', 'commentaire', 'utilisateur')
    search_fields = ('résultat', 'commentaire')
    list_filter = ('date_traitement',)


class MiseAJourRequeteAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_modif', 'commentaire', 'utilisateur', 'requete')
    search_fields = ('commentaire',)
    list_filter = ('date_modif',)


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'contenu', 'date_envoi', 'statut', 'utilisateur', 'requete')
    search_fields = ('contenu',)
    list_filter = ('date_envoi', 'statut')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'contenu', 'date_envoie', 'statut', 'utilisateur', 'requete')
    search_fields = ('contenu',)
    list_filter = ('date_envoie', 'statut')


class RequetesAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'statut', 'priorite', 'date_soumission', 'date_suppression', 'utilisateur', 'type_requete')
    search_fields = ('titre', 'descriptipn')
    list_filter = ('statut', 'priorite', 'date_soumission', 'type_requete')


class RequeteRapportAdmin(admin.ModelAdmin):
    list_display = ('id', 'requete', 'rapport')

admin.site.register(User,UserAdmin)
admin.site.register(Faculte)
admin.site.register(Departement)
admin.site.register(Filiere)
admin.site.register(TypeRequetes)
admin.site.register(Documents)
admin.site.register(Requetes)
admin.site.register(RequeteRapport)
admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(MiseAJourRequete)
admin.site.register(Rapport)
