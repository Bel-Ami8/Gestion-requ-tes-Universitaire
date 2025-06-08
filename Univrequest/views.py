from collections import defaultdict
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db.models import Q
from django.utils.timezone import now
from django.utils import timezone
from django.template.loader import get_template
from django.views.decorators.http import require_POST
import weasyprint
from django.templatetags.static import static
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
import os

from Univrequest.form import CustomUserChangeForm, CustomUserCreationForm, MessageForm, RapportForm, ReceptionnisteUserChangeForm, RequeteForm, RequeteReceptionnisteForm
from Univrequest.models import Documents, Message, Rapport, Requetes, TypeRequetes, User
from Univrequest.utils import generer_pdf_rapport


def etudiant_required(view_func):
    decorated_view_func = user_passes_test(
        lambda user: user.is_authenticated and user.is_etudiant,
        login_url='home'
    )(view_func)
    return decorated_view_func


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


@etudiant_required
def etudiant(request):
    utilisateur = request.user

    requetes_en_attentes = Requetes.objects.filter(utilisateur=utilisateur, statut='en_attente').count()
    requetes_en_cours = Requetes.objects.filter(utilisateur=utilisateur, statut='en_cours').count()
    requetes_traitees = Requetes.objects.filter(utilisateur=utilisateur, statut='traitee').count()
    requetes_rejetees = Requetes.objects.filter(utilisateur=utilisateur, statut='rejete').count()

    messages_non_lus = Message.objects.filter(destinataire=utilisateur, lu=False).count()

    context = {
        'requetes_en_attentes': requetes_en_attentes,
        'requetes_en_cours': requetes_en_cours,
        'requetes_traitees': requetes_traitees,
        'requetes_rejetees': requetes_rejetees,
        'messages_non_lus': messages_non_lus,
    }
    return render(request, 'etudiant.html', context)

@login_required
def receptionniste(request):
    admin_filiere = request.user.filiere

    # Récupérer les requêtes des étudiants de la même filière
    requetes = Requetes.objects.filter(
        utilisateur__filiere=admin_filiere,
        utilisateur__is_etudiant=True
    )

    requetes_en_cours = requetes.filter(statut='en_cours').count()
    requetes_en_att = requetes.filter(statut='en_attente').order_by('-date_creation')[:10]
    requetes_traitees = requetes.filter(statut='traitee').count()
    requetes_rejetees = requetes.filter(statut='rejete').count()
    total_requetes = requetes.count()

    # Messages non lus pour le réceptionniste
    messages_non_lus = Message.objects.filter(destinataire=request.user, lu=False).count()

    context = {
        'requetes_en_cours': requetes_en_cours,
        'requetes_en_att': requetes_en_att,
        'requetes_traitees': requetes_traitees,
        'requetes_rejetees': requetes_rejetees,
        'total_requetes': total_requetes,
        'messages_non_lus': messages_non_lus,
        'requetes': requetes.order_by('-date_creation')[:10]
        
    }
    return render(request, 'receptionniste.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('home')

@login_required
def envoyer_message(request):
    if request.method == 'GET':
        requete_id = request.GET.get('requete_id')
        initial_data = {}

        if requete_id:
            requete = get_object_or_404(Requetes, id=requete_id)
            initial_data['destinataire'] = requete.utilisateur  # automatiquement l'étudiant
        else:
            requete = None

        form = MessageForm(initial=initial_data)

        context = {
            'form': form,
            'requete': requete,
        }

        return render(request, 'messages/envoyer.html', context)
    
    elif request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.expediteur = request.user

            # Récupération sécurisée de la requête
            requete_id = request.POST.get('requete_id')
            if requete_id:
                try:
                    requete = Requetes.objects.get(id=requete_id)
                    message.requete = requete
                    message.destinataire = requete.utilisateur  # c’est ici que tu assures que le bon étudiant reçoit
                except Requetes.DoesNotExist:
                    pass

            message.save()

            fichiers = request.FILES.getlist('fichiers_upload')
            for fichier in fichiers:
                doc = Documents.objects.create(fichier=fichier, nom=fichier.name)
                message.fichiers.add(doc)

            message.save()
            return redirect('boite_de_reception')
    else:
        form = MessageForm()

    return render(request, 'messages/envoyer.html', {'form': form})


@login_required
def boite_de_reception(request):
    # Tous les messages reçus
    messages_recus = Message.objects.filter(destinataire=request.user).order_by('-date_envoie')

    # Dictionnaires pour regrouper et compter
    groupes = defaultdict(list)
    non_lus = defaultdict(int)

    for msg in messages_recus:
        expediteur = msg.expediteur
        groupes[expediteur].append(msg)
        if not msg.lu:
            non_lus[expediteur] += 1

    # Envoie au template
    return render(request, 'messages/boite_de_reception.html', {
        'groupes_messages': dict(groupes),
        'non_lus': dict(non_lus),
    })


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
            return redirect('liste_requetes')
    else:
        form = RequeteReceptionnisteForm(instance=requete)

    return render(request, 'requetes/modifier.html', {'form': form, 'requete': requete})


@login_required
def creer_requete(request):
    types_requetes = TypeRequetes.objects.all()

    if request.method == 'POST':
        # Récupérer les champs "manuellement" puisque tu n'utilises plus form.as_p
        titre = request.POST.get('titre')
        descrition = request.POST.get('descrition')
        priorite = request.POST.get('priorite')
        type_requete_id = request.POST.get('type_requete')
        fichiers = request.FILES.getlist('documents')

        # Vérifie que les champs obligatoires sont présents
        if titre and type_requete_id:
            type_requete = TypeRequetes.objects.get(pk=type_requete_id)

            requete = Requetes.objects.create(
                utilisateur=request.user,
                type_requete=type_requete,
                titre=titre,
                descrition=descrition,
                priorite=priorite
            )

            # Sauvegarder les documents
            for fichier in fichiers:
                doc = Documents.objects.create(
                    fichier=fichier,
                    nom_fichier=fichier.name,
                    chemin_fichier=fichier.name,  # ou un autre champ si tu veux stocker le chemin
                    type_fichier=fichier.content_type,
                    taille=fichier.size
                )
                requete.documents.add(doc)

            return redirect('etudiant')
    return render(request, 'requetes/creer.html', {'types_requetes': types_requetes})


@login_required
def repondre_message(request, message_id):
    message_original = get_object_or_404(Message, id=message_id)

    if request.method == "POST":
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.expediteur = request.user
            message.destinataire = message_original.expediteur
            message.requete = message_original.requete  # Ajouté pour éviter l'erreur d'intégrité
            message.save()

            # Gérer le fichier joint si présent
            if request.FILES.get('fichier'):
                Documents.objects.create(
                    message=message,
                    fichier=request.FILES['fichier'],
                    nom=request.FILES['fichier'].name
                )

            return redirect('boite_de_reception')
    else:
        form = MessageForm(initial={'sujet': f"Re: {message_original.sujet}"})

    return render(request, 'messages/repondre.html', {
        'form': form,
        'message_original': message_original,
        'destinataire_nom': message_original.expediteur.get_full_name(),
    })


@login_required
def lire_conversation(request, expediteur_id):
    user = request.user
    messages = Message.objects.filter(
        Q(expediteur__id=expediteur_id, destinataire=user) |
        Q(expediteur=user, destinataire__id=expediteur_id)
    ).order_by('date_envoie')

    # Marquer comme lus les messages que l'utilisateur a reçus
    messages.filter(destinataire=user, lu=False).update(lu=True)

    return render(request, 'messages/conversation.html', {
        'messages': messages,
        'expediteur': messages.first().expediteur if messages else None
    })


@login_required
def page_rapports(request):
    if request.method == "POST":
        periode = request.POST.get("periode")
        aujourd_hui = timezone.now().date()

        if periode == "jour":
            date_debut = date_fin = aujourd_hui
        elif periode == "semaine":
            date_debut = aujourd_hui - timedelta(days=7)
            date_fin = aujourd_hui
        elif periode == "mois":
            date_debut = aujourd_hui.replace(day=1)
            date_fin = aujourd_hui
        elif periode == "personnalise":
            date_debut = request.POST.get("date_debut")
            date_fin = request.POST.get("date_fin")
            if not date_debut or not date_fin:
                messages.error(request, "Veuillez fournir les deux dates.")
                return redirect("page_rapports")
            date_debut = datetime.strptime(date_debut, "%Y-%m-%d").date()
            date_fin = datetime.strptime(date_fin, "%Y-%m-%d").date()
        else:
            messages.error(request, "Période invalide.")
            return redirect("page_rapports")

        nom_pdf, fichier_pdf = generer_pdf_rapport(date_debut, date_fin, request.user, periode)

        rapport = Rapport.objects.create(
            periode=periode,
            date_debut=date_debut,
            date_fin=date_fin,
            filtre_description=f"Requêtes du {date_debut} au {date_fin}",
            utilisateur=request.user,
        )
        rapport.fichier_pdf.save(nom_pdf, fichier_pdf)
        messages.success(request, "Rapport généré avec succès.")
        return redirect("page_rapports")

    rapports = Rapport.objects.filter(utilisateur=request.user).order_by("-date_generation")
    paginator = Paginator(rapports, 5)
    page = request.GET.get("page")
    rapports_page = paginator.get_page(page)

    return render(request, "page_rapports.html", {"rapports": rapports_page})



@login_required
def supprimer_rapport(request, pk):
    rapport = get_object_or_404(Rapport, pk=pk, utilisateur=request.user)
    rapport.fichier_pdf.delete(save=False)
    rapport.delete()
    messages.success(request, "Rapport supprimé avec succès.")
    return redirect("page_rapports")


@login_required
def mon_compte(request):
    return render(request, 'utilisateur/mon_compte.html', {'user': request.user})

@login_required
def modifier_compte(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, "Vos informations ont été mises à jour.")
        return redirect('mon_compte')
    return render(request, 'utilisateur/modifier_compte.html', {'user': user})