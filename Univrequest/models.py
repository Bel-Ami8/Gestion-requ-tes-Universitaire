from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):# Create your models here.
   is_receptionniste = models.BooleanField(default=False)
   is_reception_departement = models.BooleanField(default=False)
   is_fac_gestionnaire = models.BooleanField(default=False)
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
        role = "Réceptionniste Central"
    elif self.is_reception_departement:
        role = "Réceptionniste Département"
    elif self.is_fac_gestionnaire:
        role = "Gestionnaire Faculté"
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

    def __str__(self):
        return f"{self.nom} - {self.departement.nom}"
