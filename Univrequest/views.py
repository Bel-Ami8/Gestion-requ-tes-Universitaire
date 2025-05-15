from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login

from Univrequest.form import CustomUserCreationForm



def home(request):
    error= ''# Create your views here.
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None :
            login(request, user)
            if user.is_etudiant:
                return redirect('etudiant')
            elif user.is_receptionniste:
                return redirect('receptionniste')
            elif user.is_reception_departement:
                return redirect('reception_depart')
            elif user.is_fac_gestionnaire:
                return redirect('fac_gestionnaire')
        else:
            error = 'mot de passe ou utilisateur incorrect'
    return render(request, 'login.html', {'error':error})


def register(request):
    form = CustomUserCreationForm()
    if request.method == "POST":
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'register.html', {'form': form})


def etudiant(request):
    return render(request,'etudiant.html')


def receptionniste(request):
    return render(request,'receptionniste.html')


def reception_depart(request):
    return render(request,'reception_depart.html')


def fac_gestionnaire(request):
    return render(request,'fac_gestionnaire.html')