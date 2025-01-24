from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse
from .models import Etudiant, Creneau, Reservation, Admin
from django.contrib.auth.hashers import check_password
from django.utils import timezone
import datetime

# Page d'accueil (simple HttpResponse, vous pouvez en faire un template si vous préférez)
def index(request):
    texte = "<h2> Réservation de Box</h2><br>"
    texte += "Bienvenue sur le site de réservation de box « silencieuses »<br><br>"
    texte += "<a href='/idEtudiant'><button>Étudiant</button></a><br>"
    texte += "<a href='/adminLogin'><button>Admin</button></a>"
    return HttpResponse(texte)

# -------------
# ÉTUDIANT
# -------------

def idEtudiant(request):
    """
    Première étape : demande du numéro étudiant.
    On envoie le formulaire à 'codeEtud'.
    """
    context = {
        'title': 'Identification Étudiant',
        'label': 'Numéro étudiant',
        'action_url': reverse('codeEtud')
    }
    return render(request, 'formEtudiant.html', context)


def codeEtud(request):
    """
    Récupère le numéro étudiant (inputEtud), le stocke en session,
    puis affiche un nouveau formulaire pour le code de vérification.
    """
    if request.method == 'POST':
        num_etud = request.POST.get('inputEtud')
        # On stocke le numéro étudiant dans la session
        request.session['NumEtud'] = num_etud

        context = {
            'title': 'Identification Étudiant',
            'label': 'Code de vérification',
            'action_url': reverse('accueilEtud'),
        }
        return render(request, 'formEtudiant.html', context)
    else:
        # Si on accède directement en GET, on redirige vers idEtudiant
        return redirect('idEtudiant')


def accueilEtud(request):
    """
    Traitement du code de vérification.
    Si le code est bon, on vérifie/crée l'étudiant en base,
    puis on l'envoie vers le calendrier ou une page d'accueil étudiant.
    """
    if request.method == 'POST':
        code = request.POST.get('inputEtud')
        if code != "0000":
            # Code erroné
            context = {
                'title': 'Erreur lors de la validation du code de vérification',
                'error': 'Code de vérification incorrect',
                'action_url': reverse('index'),
            }
            return render(request, 'erreur.html', context)
        else:
            # Code correct
            num_etud = request.session.get('NumEtud', '')
            if not num_etud:
                # Si la session est vide ou a expiré
                context = {
                    'title': 'Erreur',
                    'error': 'Numéro étudiant introuvable en session.',
                    'action_url': reverse('index'),
                }
                return render(request, 'erreur.html', context)

            # Vérifier / créer l'étudiant dans la BDD
            etudiant, created = Etudiant.objects.get_or_create(num_etudiant=num_etud)

            # On passe le numéro étudiant au template calendrier
            return render(request, 'calendrier.html', {
                'student_number': num_etud,
                'action_url': reverse('calendrier1h_to_15')  # <-- On met l'URL de la vue calendrier1h_to_15
            })

    else:
        # Si GET, on renvoie le formulaire pour le code
        context = {
            'title': 'Identification Étudiant',
            'label': 'Code de vérification',
            'action_url': reverse('accueilEtud'),
        }
        return render(request, 'formEtudiant.html', context)
    
def vueCalendrier(request):
    """
    Affiche directement la page calendrier.html (sans demander le code).
    On peut y ajouter un contrôle d'accès si nécessaire.
    """
    # Contrôle d'accès minimal : vérifier que l'utilisateur est un étudiant connecté ou un admin
    if not request.session.get('NumEtud') and not request.session.get('is_admin'):
        # Ni étudiant (session) ni admin => on redirige vers un endroit logique
        return redirect('index')

    # Passer le student_number si c'est un étudiant
    student_number = request.session.get('NumEtud')

    # Dans 'calendrier.html', vous avez <form action="{{ action_url }}">
    # => On peut définir action_url, par ex. la vue "calendrier1h_to_15"
    context = {
        'student_number': student_number,
        'action_url': reverse('calendrier1h_to_15'),
    }
    return render(request, 'calendrier.html', context)


def calendrier1h_to_15(request):
    """
    Reçoit le créneau 1h sélectionné depuis calendrier.html,
    stocke l'info en session, puis redirige vers la page calendrier15.html.
    """
    if request.method == 'POST':
        selected_slot = request.POST.get('selected_slot')  # ex: "2025-02-10 13:00"
        # On le stocke en session (ou on pourrait passer en paramètre GET)
        request.session['selected_slot'] = selected_slot

        return redirect('calendrier15')  # On va vers la vue calendrier15
    else:
        # Si on arrive en GET, on renvoie ailleurs
        return redirect('accueilEtud')

def calendrier15(request):
    """
    - GET : Affiche la page avec 2 tableaux (Box1, Box2) 
            + colorie en rouge les créneaux réservés 
            + propose un choix cliquable sur les créneaux libres.
    - POST : L'utilisateur a choisi un créneau / box => on crée la réservation.
    """
    if request.method == 'POST':
        # Traitement quand on clique sur "Valider" un sous-créneau
        chosen_creneau_id = request.POST.get('creneau_id')
        chosen_box_id = request.POST.get('box_id')
        date_chosen = request.session.get('selected_date')  # ex "2025-02-10"
        # Récupération de l'étudiant depuis la session
        student_number = request.session.get('NumEtud')

        if not (chosen_creneau_id and chosen_box_id and date_chosen and student_number):
            # Mauvais usage
            return redirect('accueilEtud')

        # Création de la réservation
        etudiant = Etudiant.objects.get(num_etudiant=student_number)
        creneau_obj = Creneau.objects.get(id=chosen_creneau_id)
        # On suppose que la table Reservation a un champ date_ (DateField),
        # creneau (FK), box_id, etc.
        Reservation.objects.create(
            etudiant=etudiant,
            box_id=int(chosen_box_id),
            creneau=creneau_obj,
            date_field=date_chosen,    # ou date_ selon votre champ
            admin_field=False
        )

        # Redirection
        return redirect('vueCalendrier')  # ou accueilEtud, etc.

    else:
        # --- GET : Affichage des 2 tableaux ---
        # On récupère la date et l'heure depuis la session
        date_chosen = request.session.get('selected_date')  # par ex "2025-02-10"
        hour_chosen = request.session.get('selected_hour')  # par ex "13:00"
        if not (date_chosen and hour_chosen):
            # Si pas de sélection, on renvoie
            return redirect('vueCalendrier')

        # On détermine quels creneaux (table Creneau) correspondent 
        # aux 4 sous-créneaux de l'heure hour_chosen. 
        # -> ex: 13:00-13:15, 13:15-13:30, 13:30-13:45, 13:45-14:00
        # 1) Soit vous avez un code pour filtrer la BDD
        #    => Si vous avez un champ heure_debut, heure_fin, etc.
        # 2) Soit vous générez 4 "heures_debut" localement, et vous faites un filter.

        base_hour = int(hour_chosen.split(':')[0])  # ex 13
        # On construit 4 sous-créneaux => ex: 13:00, 13:15, 13:30, 13:45
        from datetime import time
        sub_times = [
            (time(base_hour,  0), time(base_hour, 15)),  # 13:00 - 13:15
            (time(base_hour, 15), time(base_hour, 30)),  # 13:15 - 13:30
            (time(base_hour, 30), time(base_hour, 45)),  # 13:30 - 13:45
            (time(base_hour, 45), time(base_hour+1, 0)), # 13:45 - 14:00
        ]
        # On récupère ces creneaux dans la table Creneau
        # (ex: SELECT * FROM Creneau WHERE (heure_debut, heure_fin) in (sub_times)).
        # Selon comment vous stockez, on peut faire un "in" ou on boucle.
        # Ex. si Creneau a (heure_debut, heure_fin) = (13:00, 13:15) => on matche
        # On va faire un creneaux_sub = []
        creneaux_sub = []
        for (start, end) in sub_times:
            cr = Creneau.objects.filter(heure_debut=start, heure_fin=end).first()
            if cr:
                creneaux_sub.append(cr)

        # creneaux_sub est la liste des 4 creneaux (objets)
        # On check dans Reservation si c'est déjà pris pour date_chosen et box=1 ou 2
        reserved_box1 = set()
        reserved_box2 = set()
        # On récupère toutes les réservations pour la date et creneau__in creneaux_sub
        reservations = Reservation.objects.filter(
            date_field=date_chosen,
            creneau__in=creneaux_sub
        )
        # On remplit un set() avec creneau_id
        for r in reservations:
            if r.box_id == 1:
                reserved_box1.add(r.creneau_id)
            elif r.box_id == 2:
                reserved_box2.add(r.creneau_id)

        # On prépare la liste sub_creneaux avec info "reserved_box1" / "reserved_box2"
        sub_creneaux = []
        for c in creneaux_sub:
            sub_creneaux.append({
                'id': c.id,
                'heure_debut': c.heure_debut,
                'heure_fin': c.heure_fin,
                'reserved_for_box1': (c.id in reserved_box1),
                'reserved_for_box2': (c.id in reserved_box2),
            })

        context = {
            'date_chosen': date_chosen,
            'hour_chosen': hour_chosen,
            'sub_creneaux': sub_creneaux,
        }
        return render(request, 'calendrier15.html', context)



def profilEtudiant(request, student_number):
    """
    Affiche le profil d'un étudiant donné. 
    On filtre ses réservations en fonction de la date du jour.
    """
    etudiant = get_object_or_404(Etudiant, num_etudiant=student_number)

    # --- Contrôle d’accès ---
    is_admin = request.session.get('is_admin', False)               # bool
    current_student = request.session.get('NumEtud', '')            # ex: '12345678'

    # 2 conditions autorisées:
    #  - Admin connecté
    #  - Étudiant lui-même (session NumEtud == paramètre URL)
    if not (is_admin or current_student == student_number):
        # Ici, on bloque l’accès
        # Soit on lève une exception, soit on redirige vers une page d'erreur.
        # Exemple: on redirige vers un template "erreur.html" ou l'accueil
        return render(request, 'erreur.html', {
            'title': 'Accès refusé',
            'error': "Vous n'êtes pas autorisé à consulter ce profil.",
            'action_url': reverse('index'),  
        })

    # Réservations à venir
    reservations_a_venir = Reservation.objects.filter(
        etudiant=etudiant,
        date_field__gte=timezone.now().date()
    )

    # Réservations passées
    reservations_passees = Reservation.objects.filter(
        etudiant=etudiant,
        date_field__lt=timezone.now().date()
    )

    # Vérifier si la session contient 'is_admin'
    is_admin = request.session.get('is_admin', False)

    context = {
        'title': 'Profil Étudiant',
        'student': etudiant,
        'reservations_a_venir': reservations_a_venir,
        'reservations_passees': reservations_passees,
        'is_admin': is_admin,  # on passe True/False au template
    }
    return render(request, 'profilEtudiant.html', context)


# -------------
# ADMIN
# -------------

def adminLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Récupérer le compte admin
        admin_user = Admin.objects.filter(identifiant=username).first()

        if admin_user:
            # Vérifier le mot de passe haché
            if password == admin_user.mdp:
                # Succès : on stocke is_admin = True en session
                request.session['is_admin'] = True
                # Redirection vers la page d'accueil admin (ou une autre)
                return redirect('accueilAdmin')
            else:
                # Mauvais mot de passe
                context = {
                    'error': 'Mot de passe incorrect.',
                }
                return render(request, 'adminLogin.html', context)
        else:
            # Identifiant inconnu
            context = {
                'error': 'Cet identifiant admin est inconnu.',
            }
            return render(request, 'adminLogin.html', context)

    else:
        # GET : on affiche le formulaire
        return render(request, 'adminLogin.html')



def accueilAdmin(request):
    """
    Accueil Admin : par exemple un calendrierAdmin ou un tableau de bord.
    """
    if not request.session.get('is_admin', False):
        # Accès refusé
        return redirect('adminLogin')

    # Sinon, on affiche la page admin
    context = {
        'title': 'Gestion des réservations - Admin',
        'action_url': reverse('accueilAdmin'),
    }
    return render(request, 'calendrierAdmin.html', context)


def profilAdmin(request):
    """
    Affiche la liste des étudiants + les réservations du jour.
    """
    # Récupération de tous les étudiants
    students = Etudiant.objects.all()

    # Pour la démonstration, vous utilisez 'Reservation.objects.filter(date=...)'
    # mais dans votre modèle, vous avez 'date_field' -> Vérifiez la cohérence
    reservations_today = Reservation.objects.filter(date_field=timezone.now().date())

    context = {
        'title': 'Profil Admin',
        'students': students,
        'reservations_today': reservation_jour,
    }
    return render(request, 'profilAdmin.html', context)



def toggleBlockStudent(request, student_number):
    """
    Bloquer / Débloquer un étudiant (changement du champ 'autorise').
    """
    etudiant = get_object_or_404(Etudiant, num_etudiant=student_number)
    etudiant.autorise = not etudiant.autorise
    etudiant.save()
    return redirect('profilEtudiant', student_number=student_number)
