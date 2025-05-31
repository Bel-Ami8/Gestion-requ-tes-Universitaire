from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from Univrequest.views import home,register,receptionniste,etudiant

urlpatterns = [
    path("", views.home, name="home"),
    path("register", views.register, name="register"),
    path("receptionniste", views.receptionniste, name="receptionniste"),
    path("etudiant", views.etudiant, name="etudiant"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path('envoyer/', views.envoyer_message, name='envoyer_message'),
    path('boite/', views.boite_de_reception, name='boite_de_reception'),
    path('utilisateurs/', views.gerer_utilisateurs, name='gestion_utilisateurs'),
    path('utilisateurs/<int:user_id>/modifier/', views.modifier_utilisateur, name='modifier_utilisateur'),
    path('utilisateurs/<int:user_id>/supprimer/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
    path('requetes/', views.lister_requetes, name='lister_requetes'),
    path('requetes/<int:requete_id>/', views.detail_requete, name='detail_requete'),
    path('requetes/<int:requete_id>/modifier/', views.modifier_requete, name='modifier_requete'),
]
