from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout

from Univrequest.form import CustomUserCreationForm



def home(request):
    if request.user.is_authenticated:
        # Redirige directement vers la page utilisateur appropriée
        if request.user.is_etudiant:
            return redirect('etudiant')
        elif request.user.is_receptionniste:
            return redirect('receptionniste')
        # ou render une autre page d'accueil
    else:
        # Sinon, affiche la page de login
        error = ''
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_etudiant:
                    return redirect('etudiant')
                elif user.is_receptionniste:
                    return redirect('receptionniste')
            else:
                error = 'mot de passe ou utilisateur incorrect'
        return render(request, 'login.html', {'error': error})




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


def logout_view(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('home')