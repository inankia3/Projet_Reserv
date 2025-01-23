from django.db import models


class Etudiant(models.Model):
    num_etudiant = models.CharField(unique=True, max_length=8)
    autorise = models.BooleanField(blank=True, null=True)
    date_derniere_reserv = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Etudiant'


class Creneau(models.Model):
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

    class Meta:
        managed = False
        db_table = 'Creneau'

class Reservation(models.Model):
    etudiant = models.ForeignKey('Etudiant', models.DO_NOTHING)
    box_id = models.IntegerField()
    date_field = models.DateField(db_column='date_')  # Field renamed because it ended with '_'.
    creneau = models.ForeignKey('Creneau', models.DO_NOTHING)
    admin_field = models.BooleanField(db_column='admin_')  # Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'Reservation'


class Admin(models.Model):
    identifiant = models.CharField(max_length=50)
    mdp = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'Admin'