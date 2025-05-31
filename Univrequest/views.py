from django.shortcuts import get_object_or_404, render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from Univrequest.form import CustomUserChangeForm, CustomUserCreationForm, MessageForm, ReceptionnisteUserChangeForm, RequeteReceptionnisteForm
from Univrequest.models import Documents, Message, Requetes, User



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


def envoyer_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            # Créer le message sans encore enregistrer les fichiers
            message = form.save(commit=False)
            message.expediteur = request.user
            message.save()
            form.save_m2m()  # Sauvegarde des relations M2M classiques si besoin

            # Gestion des fichiers uploadés
            fichiers = request.FILES.getlist('fichiers_upload')
            for fichier in fichiers:
                doc = Documents.objects.create(fichier=fichier, nom=fichier.name)
                message.fichiers.add(doc)

            message.save()
            return redirect('boite_de_reception')  # Ton URL de redirection
    else:
        form = MessageForm()
    return render(request, 'messages/envoyer.html', {'form': form})

@login_required
def boite_de_reception(request):
    messages = Message.objects.filter(destinataire=request.user).order_by('-date_envoie')
    messages.filter(lu=False).update(lu=True)
    return render(request, 'messages/boite_de_reception.html', {'messages': messages})


def dashboard_etudiant(request):
    user = request.user
    
    # Exemple du compteur pour l'utilisateur connecté
    messages_non_lus = Message.objects.filter(destinataire=user, lu=False).count()

    # Les autres compteurs
    requetes_en_cours = Requetes.objects.filter(user=user, statut='en_cours').count()
    requetes_traitees = Requetes.objects.filter(user=user, statut='traite').count()

    context = {
        'requetes_en_cours': requetes_en_cours,
        'requetes_traitees': requetes_traitees,
        'messages_non_lus': messages_non_lus,
        # ... autres variables si besoin
    }
    return render(request, 'etudiant.html', context)


@login_required
def lire_message(request, message_id):
    """
    Vue pour lire un message individuel.
    Elle marque le message comme lu et l'affiche à l'utilisateur.
    """

    # Vérifie que le message appartient bien au destinataire connecté
    message = get_object_or_404(Message, id=message_id, destinataire=request.user)

    # Marquer le message comme lu s'il ne l'est pas déjà
    if not message.lu:
        message.lu = True
        message.save()

    # Préparer le contexte pour l'affichage du message
    context = {
        'message': message
    }

    # Afficher le message dans le template "lire_message.html"
    return render(request, 'messages/lire_message.html', context)


@login_required
def admin_dashboard(request):
    # Filtrage des requêtes selon la filière de l’admin
    admin_filiere = request.user.filiere
    requetes = Requetes.objects.filter(etudiant__filiere=admin_filiere)

    requetes_en_attente = requetes.filter(statut='en_cours').count()
    requetes_traitees = requetes.filter(statut='traite').count()
    total_requetes = requetes.count()
    
    # Messages non lus pour l’admin
    messages_non_lus = Message.objects.filter(destinataire=request.user, lu=False).count()

    context = {
        'requetes_en_attente': requetes_en_attente,
        'requetes_traitees': requetes_traitees,
        'total_requetes': total_requetes,
        'messages_non_lus': messages_non_lus,
        'requetes': requetes.order_by('-date_creation')[:10]
    }
    return render(request, 'receptionniste.html', context)


def is_receptionniste(user):
    return user.is_authenticated and user.is_receptionniste

@login_required
def gerer_utilisateurs(request):
    if not request.user.is_receptionniste:
        messages.error(request, "Accès refusé.")
        return redirect('home')

    # Affiche les étudiants de la même filière que le réceptionniste
    etudiants = User.objects.filter(is_etudiant=True, filiere=request.user.filiere)
    return render(request, 'gestion_utilisateurs.html', {'etudiants': etudiants})

@login_required
def modifier_utilisateur(request, user_id):
    if not request.user.is_receptionniste:
        messages.error(request, "Accès refusé.")
        return redirect('home')

    etudiant = get_object_or_404(User, id=user_id, is_etudiant=True, filiere=request.user.filiere)
    if request.method == 'POST':
        form = ReceptionnisteUserChangeForm(request.POST, instance=etudiant)
        if form.is_valid():
            form.save()
            messages.success(request, "Étudiant mis à jour avec succès.")
            return redirect('gestion_utilisateurs')
    else:
        form = ReceptionnisteUserChangeForm(instance=etudiant)

    return render(request, 'modifier_utilisateur.html', {'form': form, 'etudiant': etudiant})

@login_required
def supprimer_utilisateur(request, user_id):
    if not request.user.is_receptionniste:
        messages.error(request, "Accès refusé.")
        return redirect('home')

    etudiant = get_object_or_404(User, id=user_id, is_etudiant=True, filiere=request.user.filiere)
    etudiant.delete()
    messages.success(request, "Étudiant supprimé avec succès.")
    return redirect('gestion_utilisateurs')

@login_required
def liste_utilisateurs(request):
    if not is_receptionniste(request.user):
        messages.error(request, "Accès refusé.")
        return redirect('home')

    # Le réceptionniste ne peut voir que les étudiants de sa filière
    utilisateurs = User.objects.filter(is_etudiant=True, filiere=request.user.filiere)

    context = {
        'utilisateurs': utilisateurs,
    }
    return render(request, 'liste_utilisateurs.html', context)


@login_required
def lister_requetes(request):
    if not request.user.is_receptionniste:
        messages.error(request, "Accès refusé.")
        return redirect('home')

    requetes = Requetes.objects.filter(utilisateur__filiere=request.user.filiere)
    return render(request, 'requetes/lister.html', {'requetes': requetes})


@login_required
def detail_requete(request, requete_id):
    if not request.user.is_receptionniste:
        messages.error(request, "Accès refusé.")
        return redirect('home')

    requete = get_object_or_404(Requetes, id=requete_id, utilisateur__filiere=request.user.filiere)
    return render(request, 'requetes/detail.html', {'requete': requete})


@login_required
def modifier_requete(request, requete_id):
    if not request.user.is_receptionniste:
        messages.error(request, "Accès refusé.")
        return redirect('home')

    requete = get_object_or_404(Requetes, id=requete_id, utilisateur__filiere=request.user.filiere)

    if request.method == 'POST':
        form = RequeteReceptionnisteForm(request.POST, instance=requete)
        if form.is_valid():
            form.save()
            messages.success(request, "Requête mise à jour avec succès.")
            return redirect('lister_requetes')
    else:
        form = RequeteReceptionnisteForm(instance=requete)

    return render(request, 'requetes/modifier.html', {'form': form, 'requete': requete})
