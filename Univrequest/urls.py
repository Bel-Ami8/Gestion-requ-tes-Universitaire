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
]
