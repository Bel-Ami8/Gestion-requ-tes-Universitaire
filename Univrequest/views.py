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
