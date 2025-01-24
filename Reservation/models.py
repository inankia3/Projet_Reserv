from django.db import models
from django.utils import timezone

class Etudiant(models.Model):
    num_etudiant = models.CharField(unique=True, max_length=8)
    autorise = models.BooleanField(default=True)
    # date_derniere_reserv étant NOT NULL en base, on met un default
    date_derniere_reserv = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'Etudiant'

    def __str__(self):
        return f"Étudiant {self.num_etudiant}"


class Creneau(models.Model):
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

    class Meta:
        managed = False
        db_table = 'Creneau'

    def __str__(self):
        return f"{self.heure_debut} - {self.heure_fin}"


class Reservation(models.Model):
    etudiant = models.ForeignKey('Etudiant', models.DO_NOTHING)
    box_id = models.IntegerField()
    # On fait correspondre la colonne 'date_' à l’attribut date_reservation
    date_field= models.DateField(db_column='date_')
    creneau = models.ForeignKey('Creneau', models.DO_NOTHING)
    admin_field = models.BooleanField(db_column='admin_')

    class Meta:
        managed = False
        db_table = 'Reservation'

    def __str__(self):
        return f"Reservation de {self.etudiant} le {self.date_reservation}"


class Admin(models.Model):
    identifiant = models.CharField(max_length=200)
    mdp = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'Admin'

    def __str__(self):
        return f"Admin {self.identifiant}"
