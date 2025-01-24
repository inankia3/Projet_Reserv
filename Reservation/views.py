from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse
from .models import Etudiant, Creneau, Reservation, Admin
from django.contrib.auth.hashers import make_password, check_password
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
    Affiche 4 sous-créneaux de 15min pour l'heure choisie.
    À la validation, on crée la réservation en base
    puis on redirige vers calendrier.html (ou accueilEtud).
    """
    if request.method == 'POST':
        # L'utilisateur a choisi un sous-créneau final (ex "13:00-13:15")
        final_slot = request.POST.get('final_slot')
        student_number = request.session.get('NumEtud')  # Supposez que vous l'avez en session
        selected_slot = request.session.get('selected_slot')  # ex "2025-02-10 13:00"

        if not (final_slot and student_number and selected_slot):
            # Mauvais usage, on retourne
            return redirect('accueilEtud')

        # Décomposer final_slot (ex "13:00-13:15")
        start_str, end_str = final_slot.split('-')  # "13:00" / "13:15"
        start_str = start_str.strip()
        end_str = end_str.strip()

        # Décomposer selected_slot (ex "2025-02-10 13:00")
        date_str, hour_str = selected_slot.split(' ')
        # date_str = "2025-02-10", hour_str = "13:00"

        # Construire datetime pour début et fin
        dt_format = "%Y-%m-%d %H:%M"
        dt_debut_str = f"{date_str} {start_str}"
        dt_fin_str   = f"{date_str} {end_str}"

        dt_debut = datetime.datetime.strptime(dt_debut_str, dt_format)
        dt_fin   = datetime.datetime.strptime(dt_fin_str, dt_format)

        # Créer la réservation (ex: on suppose un modèle Reservation avec date_reservation, heure_debut, heure_fin, etc.)
        etudiant = Etudiant.objects.get(num_etudiant=student_number)

        # Récupérer l'ID du créneau correspondant à l'heure de début
        creneau_id = Creneau.objects.get(heure_debut=dt_debut.time())

        Reservation.objects.create(
            etudiant=etudiant,
            box_id=1,             # ex. box 1 par défaut
            admin_field=False,    # champ bool
            date_field=dt_debut.date(),
            creneau= creneau_id,
        )

        # Mettre à jour l'étudiant (date_derniere_reserv, etc.)
        etudiant.date_derniere_reserv = timezone.now()
        etudiant.save()

        # Rediriger vers calendrier.html ou accueilEtud
        return redirect('profilEtudiant', student_number=student_number)

    else:
        # GET : on affiche la liste des 4 sous-créneaux
        selected_slot = request.session.get('selected_slot')  # "2025-02-10 13:00"
        sub_slots = []
        if selected_slot:
            # On récupère l'heure
            _, hour_str = selected_slot.split(' ')  # ex "13:00"
            base_hour = int(hour_str.split(':')[0])  # 13
            # exemple : "13:00-13:15", "13:15-13:30", ...
            sub_slots = [
                f"{base_hour:02d}:00 - {base_hour:02d}:15",
                f"{base_hour:02d}:15 - {base_hour:02d}:30",
                f"{base_hour:02d}:30 - {base_hour:02d}:45",
                f"{base_hour:02d}:45 - {base_hour+1:02d}:00",
            ]

        context = {
            'sub_slots': sub_slots,
            'selected_slot': selected_slot,
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
        admin_user = Admin.objects.filter(identifiant=username).first()

        if admin_user and check_password(password, admin_user.mdp):
            # Connexion réussie : on met un flag dans la session
            request.session['is_admin'] = True
            return redirect('accueilAdmin')
        else:
            context = {
                'title': 'Connexion Admin',
                'error': 'Identifiants incorrects',
            }
            return render(request, 'adminLogin.html', context)
    else:
        context = {
            'title': 'Connexion Admin',
        }
        return render(request, 'adminLogin.html', context)



def accueilAdmin(request):
    """
    Accueil Admin : par exemple un calendrierAdmin ou un tableau de bord.
    """
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
        'reservations_today': reservations_today,
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
