from django.urls import path
from . import views
from Univrequest.views import home,register,receptionniste,etudiant,reception_depart,fac_gestionnaire

urlpatterns = [
    path("", views.home, name="home"),
    path("register", views.register, name="register"),
    path("receptionniste", views.receptionniste, name="receptionniste"),
    path("etudiant", views.etudiant, name="etudiant"),
    path("reception_depart", views.reception_depart, name="reception_depart"),
    path("fac_gestionnaire", views.fac_gestionnaire, name="fac_gestionnaire"),
]
