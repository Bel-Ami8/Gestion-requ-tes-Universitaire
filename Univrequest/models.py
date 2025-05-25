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
