from django.contrib import admin
from .models import Etudiant, Creneau, Reservation, Admin

# Enregistre les modèles pour qu'ils soient visibles dans l'interface d'administration
admin.site.register(Etudiant)
admin.site.register(Creneau)
admin.site.register(Reservation)
admin.site.register(Admin)