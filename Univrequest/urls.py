from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from Univrequest.views import home, modifier_compte, mon_compte, page_rapports,register,receptionniste,etudiant

urlpatterns = [
    path("", views.home, name="home"),
    path("register", views.register, name="register"),
    path("receptionniste", views.receptionniste, name="receptionniste"),
    path("etudiant", views.etudiant, name="etudiant"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path('envoyer/', views.envoyer_message, name='envoyer_message'),
    path('boite/', views.boite_de_reception, name='boite_de_reception'),
    path('conversation/<int:expediteur_id>/', views.lire_conversation, name='lire_conversation'),
    path('message/<int:message_id>/', views.lire_message, name='lire_message'),
    path('messages/repondre/<int:message_id>/', views.repondre_message, name='repondre_message'),
    path('utilisateurs/', views.gerer_utilisateurs, name='gestion_utilisateurs'),
    path('utilisateurs/<int:user_id>/modifier/', views.modifier_utilisateur, name='modifier_utilisateur'),
    path('utilisateurs/<int:user_id>/supprimer/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
    path('requetes/', views.lister_requetes, name='liste_requetes'),
    path('requetes/<int:requete_id>/', views.detail_requete, name='detail_requete'),
    path('requetes/<int:requete_id>/modifier/', views.modifier_requete, name='modifier_requete'),
    path('requetes/creer/', views.creer_requete, name='creer_requete'),
    path("rapports/", views.page_rapports, name="page_rapports"),
    path("rapports/supprimer/<int:pk>/", views.supprimer_rapport, name="supprimer_rapport"),
    path('compte/', mon_compte, name='mon_compte'),
    path('compte/modifier/', modifier_compte, name='modifier_compte'),

]
