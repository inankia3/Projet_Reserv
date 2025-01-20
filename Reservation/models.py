from django.db import models

class Box(models.Model):
    numero = models.IntegerField()
    bat_nom = models.CharField(max_length=20)

class Etudiant(models.Model):
    num_etudiant = models.CharField(max_length=255, unique=True)
    autorise = models.BooleanField(default=True)
    date_derniere_reserv = models.DateTimeField()

class Creneau(models.Model):
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.heure_debut >= self.heure_fin:
            raise ValidationError('L\'heure de début doit être inférieure à l\'heure de fin.')

class Reservation(models.Model):
    STATUT_CHOICES = [
        ('passee', 'Passée'),
        ('en_cours', 'En cours'),
        ('a_venir', 'À venir'),
    ]

    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    box = models.ForeignKey(Box, on_delete=models.CASCADE)
    date = models.DateField()
    creneau = models.ForeignKey(Creneau, on_delete=models.CASCADE)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='a_venir')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('etudiant', 'box', 'date', 'creneau')
