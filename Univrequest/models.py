from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):# Create your models here.
   is_receptionniste = models.BooleanField(default=False)
   is_etudiant = models.BooleanField(default=True)
   
   matricule = models.CharField(max_length=30, unique=True, null=True, blank=True)  # seulement pour étudiant
   faculte = models.ForeignKey('Faculte', on_delete=models.SET_NULL, null=True, blank=True)
   departement = models.ForeignKey('Departement', on_delete=models.SET_NULL, null=True, blank=True)
   filiere = models.ForeignKey('Filiere', on_delete=models.SET_NULL, null=True, blank=True)
   niveau = models.CharField(max_length=10, choices=[
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'),
        ('L3', 'Licence 3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
        ('Doc', 'Doctorat'),
    ], null=True, blank=True)
   
   def __str__(self):
    if self.is_etudiant:
        role = "Étudiant"
    elif self.is_receptionniste:
        role = "Réceptionniste"
    else:
        role = "Utilisateur"
    return f"{self.username} ({role})"


class Faculte(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Departement(models.Model):
    nom = models.CharField(max_length=100)
    faculte = models.ForeignKey(Faculte, on_delete=models.CASCADE, related_name='departements')

    def __str__(self):
        return f"{self.nom} - {self.faculte.nom}"


class Filiere(models.Model):
    nom = models.CharField(max_length=100)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, related_name='filieres')
    receptionniste = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'is_receptionniste': True},  # filtrer seulement les réceptionnistes
        related_name='filieres_assignees')
    def __str__(self):
        return f"{self.nom} - {self.departement.nom}"

class Requetes(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type_requete = models.ForeignKey('TypeRequetes', on_delete=models.CASCADE, blank=False, null=False)

    titre = models.CharField(max_length=100)
    descrition = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_suppression = models.DateTimeField(blank=True, null=True)
    PRIORITE_CHOICES = [
        ('faible', 'Faible'),
        ('moyenne', 'Moyenne'),
        ('haute', 'Haute')
    ]
    priorite = models.CharField(max_length=10, choices=PRIORITE_CHOICES, default='moyenne')

    # Statut
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('traitee', 'Traité'),
        ('rejete', 'Rejeté')
    ]
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='en_attente')
    documents = models.ManyToManyField('Documents', blank=True, related_name='requete_documents')

    def __str__(self):
        return self.titre


class TypeRequetes(models.Model):
    libelle = models.CharField(max_length=255)

    def __str__(self):
        return self.libelle


class Documents(models.Model):
    fichier = models.FileField(upload_to='documents/')
    nom_fichier = models.CharField(max_length=255)
    chemin_fichier = models.CharField(max_length=255)
    type_fichier = models.CharField(max_length=50)
    taille = models.IntegerField()
    date_ajout = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.nom_fichier

class Rapport(models.Model):
    date_generation = models.DateTimeField(auto_now_add=True)
    periode = models.CharField(max_length=50, choices=[
        ('jour', 'Jour'),
        ('semaine', 'Semaine'),
        ('mois', 'Mois'),
        ('personnalise', 'Date spécifique'),
    ])
    date_debut = models.DateField()
    date_fin = models.DateField()
    filtre_description = models.TextField()  # Résumé des critères
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fichier_pdf = models.FileField(upload_to='rapports_pdfs/')

    def __str__(self):
        return f"Rapport généré le {self.date_generation.strftime('%d/%m/%Y')} par {self.utilisateur}"


class MiseAJourRequete(models.Model):
    date_modif = models.DateTimeField(auto_now=True)
    commentaire = models.TextField(blank=True, null=True)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    requete = models.ForeignKey('Requetes', on_delete=models.CASCADE)

    def __str__(self):
        return f"Mise à jour {self.id} - {self.requete.titre}"


class Notification(models.Model):
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50, choices=[('non_lu', 'Non lu'), ('lu', 'Lu')], default='non_lu')
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    requete = models.ForeignKey('Requetes', on_delete=models.CASCADE)

    def __str__(self):
        return f"Notification {self.id} - {self.utilisateur.username}"


class RequeteRapport(models.Model):
    requete = models.ForeignKey('Requetes', on_delete=models.CASCADE)
    rapport = models.ForeignKey('Rapport', on_delete=models.CASCADE)

    def __str__(self):
        return f"RequeteRapport - {self.requete.titre} / {self.rapport.id}"


class Message(models.Model):
    contenu = models.TextField()
    date_envoie = models.DateTimeField(auto_now_add=True)
    sujet = models.CharField(max_length=255, blank=True)
    statut = models.CharField(max_length=50, choices=[('envoye', 'Envoyé'), ('recu', 'Reçu')], default='envoye')
    expediteur = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages_envoyes', on_delete=models.CASCADE)
    destinataire = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages_recus', on_delete=models.CASCADE)
    requete = models.ForeignKey('Requetes', on_delete=models.CASCADE)
    lu = models.BooleanField(default=False)
    fichiers = models.ManyToManyField('Documents', blank=True) 

    def __str__(self):
        return f"De {self.expediteur} à {self.destinataire} - {self.date_envoie}"
