
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Etudiant, Creneau, Reservation, Admin
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse

import re
import datetime
# Page d'accueil (simple HttpResponse, vous pouvez en faire un template si vous préférez)
def index(request):
    return render(request, 'index.html')

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
    if request.method == 'POST':
        num_etud = request.POST.get('inputEtud')

        # Vérifier que le numéro étudiant est un nombre à 8 chiffres
        if not re.match(r'^\d{8}$', num_etud):
            context = {
                'title': 'Erreur de format',
                'error': 'Ce numéro étudiant n\'existe pas',
                'action_url': reverse('idEtudiant'),
            }
            return render(request, 'erreur.html', context)

        # Vérifier si l'étudiant existe déjà dans la base de données
        try:
            etudiant = Etudiant.objects.get(num_etudiant=num_etud)
        except Etudiant.DoesNotExist:
            # Si l'étudiant n'existe pas, le créer avec une date_derniere_reserv standardisée pour éviter les erreurs
            etudiant = Etudiant.objects.create(
                num_etudiant=num_etud,
                autorise=True,
                date_derniere_reserv=datetime.datetime(1970, 1, 1, 0, 0, 0)  # 1er janvier de l'année 1970 à 00:00
            )

        # Stocker le numéro étudiant en session
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
            request.session['is_admin'] = False
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

            # Vérifier si l'étudiant a été bloqué par un admin
            etudiant = Etudiant.objects.get(num_etudiant=num_etud)
            if not etudiant.autorise:
                # Étudiant bloqué
                context = {
                    'title': 'Accès refusé',
                    'error': 'Vous avez été interdit de réservation de box pour mauvais comportement. Veuillez contacter la responsable de la bibliothèque pour plus d\'informations.',
                    'action_url': reverse('index'),
                }
                return render(request, 'erreur.html', context)

            # Si l'étudiant n'est pas bloqué, continuer
            return render(request, 'calendrier.html', {
                'student_number': num_etud,
                'action_url': reverse('calendrier1h_to_15'),
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
    """
    # Contrôle d'accès minimal : vérifier que l'utilisateur est un étudiant connecté ou un admin
    if not request.session.get('NumEtud') and not request.session.get('is_admin'):
        # Ni étudiant (session) ni admin => on redirige vers un endroit logique
        return redirect('index')

    # Passer le student_number si c'est un étudiant
    student_number = request.session.get('NumEtud')

    context = {
        'student_number': student_number,
        'action_url': reverse('calendrier1h_to_15'),
    }
    return render(request, 'calendrier.html', context)



def calendrier1h_to_15(request):
    if request.method == 'POST':
        # Récupérer le créneau choisi (date + heure) depuis le champ hidden 'selected_slot'
        selected_slot = request.POST.get('selected_slot')  # ex: "2025-02-10 13:00"
        # Stocker en session pour l'utiliser dans calendrier15
        if selected_slot:
            date_str, hour_str = selected_slot.split(' ')
            request.session['selected_date'] = date_str
            request.session['selected_hour'] = hour_str
        # Rediriger vers la vue calendrier15
        return redirect('calendrier15')
    else:
        # Si on arrive en GET, on renvoie par exemple vers la page calendrier
        return redirect('vueCalendrier')

def calendrier15(request):
    if request.method == 'POST':
        chosen_creneau_id = request.POST.get('creneau_id')
        chosen_box_id = request.POST.get('box_id')
        date_chosen = request.session.get('selected_date')
        student_number = request.session.get('NumEtud')

        if not (chosen_creneau_id and chosen_box_id and date_chosen and student_number):
            return redirect('accueilEtud')

        etudiant = Etudiant.objects.get(num_etudiant=student_number)

        # Vérifier les conditions de réservation
        maintenant = timezone.now()

        delai_24h = etudiant.date_derniere_reserv + timedelta(hours=24)

        # Compter les réservations à venir
        reservations_a_venir = Reservation.objects.filter(
            etudiant=etudiant,
            date_field__gte=maintenant.date()
        ).count()

        if maintenant < delai_24h:
            # L'étudiant a déjà réservé dans les dernières 24 heures
            delai_restant = delai_24h - maintenant
            heures_restantes = delai_restant.seconds // 3600
            minutes_restantes = (delai_restant.seconds % 3600) // 60
            message = f"Vous ne pouvez réserver qu'une fois toutes les 24 heures. Temps restant : {heures_restantes}h {minutes_restantes}min."
            return render(request, 'calendrier.html', {
                'student_number': student_number,
                'action_url': reverse('calendrier1h_to_15'),
                'error_message': message,
            })

        if reservations_a_venir >= 2:
            # L'étudiant a déjà 2 réservations à venir
            message = "Vous ne pouvez pas avoir plus de 2 réservations à venir."
            return render(request, 'calendrier.html', {
                'student_number': student_number,
                'action_url': reverse('calendrier1h_to_15'),
                'error_message': message,
            })

        # Si les conditions sont remplies, créer la réservation
        creneau_obj = Creneau.objects.get(id=chosen_creneau_id)
        Reservation.objects.create(
            etudiant=etudiant,
            box_id=int(chosen_box_id),
            creneau=creneau_obj,
            date_field=date_chosen,
            admin_field=False
        )

        # Mettre à jour la date de la dernière réservation
        etudiant.date_derniere_reserv = maintenant
        etudiant.save()

        # Ajouter les informations de réservation dans le contexte
        context = {
            'reservation_confirmed': True,
            'reservation_date': date_chosen,
            'reservation_time': f"{creneau_obj.heure_debut} - {creneau_obj.heure_fin}",
            'reservation_box': chosen_box_id,
            'student_number': student_number,
        }
        return render(request, 'calendrier15.html', context)

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

        base_hour = int(hour_chosen.split(':')[0])  # ex 13
        # On construit 4 sous-créneaux => ex: 13:00, 13:15, 13:30, 13:45
        from datetime import time
        sub_times = [
            (time(base_hour,  0), time(base_hour, 15)),  # 13:00 - 13:15
            (time(base_hour, 15), time(base_hour, 30)),  # 13:15 - 13:30
            (time(base_hour, 30), time(base_hour, 45)),  # 13:30 - 13:45
            (time(base_hour, 45), time(base_hour+1, 0)), # 13:45 - 14:00
        ]
        # On récupère ces creneaux dans la table Creneau avec une boucle
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
                'reserved_for_box1': (c.id in reserved_box1), #booleen
                'reserved_for_box2': (c.id in reserved_box2),
            })

        context = {
            'date_chosen': date_chosen,
            'hour_chosen': hour_chosen,
            'sub_creneaux': sub_creneaux,
        }
        return render(request, 'calendrier15.html', context)



def profilEtudiant(request, student_number):
    etudiant = get_object_or_404(Etudiant, num_etudiant=student_number)

    # Contrôle d’accès
    is_admin = request.session.get('is_admin', False)
    current_student = request.session.get('NumEtud', '')
    if not (is_admin or current_student == student_number):
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

    context = {
        'title': 'Profil Étudiant',
        'student': etudiant,
        'reservations_a_venir': reservations_a_venir,
        'reservations_passees': reservations_passees,
        'is_admin': is_admin,
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
    Accueil Admin : calendrier
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

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin', False):
            return redirect('adminLogin')
        return view_func(request, *args, **kwargs)
    return wrapper

@admin_required
def profilAdmin(request):
    """
    Affiche :
      - la liste de tous les étudiants
      - les réservations de la semaine qui ne sont pas bloquée par un admin (admin_field=False)
      Si on est samedi ou dimanche, on affiche les réservations de la semaine suivante.
    """
    # Récupérer tous les étudiants
    students = Etudiant.objects.all().order_by('num_etudiant')

    # Déterminer le début de la semaine (lundi)
    today = timezone.now().date()
    current_day = today.weekday()  # 0=Lundi, 1=Mardi, ..., 6=Dimanche

    # Si on est samedi (5) ou dimanche (6), on affiche la semaine suivante
    if current_day >= 5:  # Samedi ou dimanche
        start_of_week = today + timedelta(days=(7 - current_day))  # Lundi suivant
    else:
        start_of_week = today - timedelta(days=current_day)  # Lundi de la semaine en cours

    end_of_week = start_of_week + timedelta(days=6)  # Dimanche de la semaine

    # Récupérer les réservations de la semaine (admin_field=False => vraies réservations d'étudiant)
    reservations_week = Reservation.objects.filter(
        date_field__range=[start_of_week, end_of_week],
        admin_field=False
    ).order_by('date_field', 'creneau__heure_debut')

    # Séparer les réservations par box
    reservations_box1 = reservations_week.filter(box_id=1)
    reservations_box2 = reservations_week.filter(box_id=2)

    context = {
        'title': 'Profil Admin',
        'students': students,
        'reservations_box1': reservations_box1,
        'reservations_box2': reservations_box2,
        'start_of_week': start_of_week,
        'end_of_week': end_of_week,
    }
    return render(request, 'profilAdmin.html', context)


def blockSlotsAdmin(request):
    """
    Reçoit en POST `selected_hours` (ex: "2025-02-10 09:00,2025-02-10 10:00") 
    + which_box ("1","2","both").
    Pour chaque créneau d'une heure, on crée 4 (ou 8) reservations admin_field=True.
    Si un créneau est déjà réservé par un étudiant, on annule cette réservation
    et on réinitialise sa date_derniere_reserv.
    """
    if request.method == 'POST':
        selected_hours = request.POST.get('selected_hours', '').strip()
        which_box = request.POST.get('which_box', '').strip()  # "1","2","both"

        if not selected_hours:
            return redirect('accueilAdmin')

        list_slots = selected_hours.split(',')  # ex. ["2025-02-10 09:00", ...]

        for slot in list_slots:
            slot = slot.strip()
            date_str, hour_str = slot.split(' ')
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            h, m = hour_str.split(':')
            hour_int = int(h)

            # On trouve le premier creneau 15 min => hour_int:00 -> hour_int:15
            heure_debut = datetime.time(hour_int, 0)
            heure_fin = (datetime.datetime.combine(date_obj, heure_debut)
                         + datetime.timedelta(minutes=15)).time()

            first_creneau = Creneau.objects.filter(
                heure_debut=heure_debut,
                heure_fin=heure_fin
            ).first()

            if not first_creneau:
                # ne pas planter, on skip
                continue

            # On crée 4 ou 8 reservations
            # => offset = 0..3 => creneau_id = first_creneau.id + offset
            # => si which_box = "1", on fait box_id=1
            # => si which_box = "2", box_id=2
            # => si "both", on fait 2 reservations par offset: box1 + box2

            for offset in range(4):
                creneau_id = first_creneau.id + offset

                # Annuler les réservations étudiantes existantes pour ce créneau
                reservations_etudiantes = Reservation.objects.filter(
                    date_field=date_obj,
                    creneau_id=creneau_id,
                    admin_field=False  # Seulement les réservations étudiantes
                )

                # Réinitialiser la date_derniere_reserv des étudiants concernés
                for reservation in reservations_etudiantes:
                    etudiant = reservation.etudiant
                    etudiant.date_derniere_reserv = datetime.datetime(1970, 1, 1, 0, 0, 0)  # Date par défaut
                    etudiant.save()

                # Supprimer les réservations étudiantes
                reservations_etudiantes.delete()

                if which_box == "1":
                    Reservation.objects.create(
                        etudiant_id=None,
                        box_id=1,
                        date_field=date_obj,
                        creneau_id=creneau_id,
                        admin_field=True
                    )
                elif which_box == "2":
                    Reservation.objects.create(
                        etudiant_id=None,
                        box_id=2,
                        date_field=date_obj,
                        creneau_id=creneau_id,
                        admin_field=True
                    )
                elif which_box == "both":
                    # 2 reservations (box1 + box2)
                    Reservation.objects.create(
                        etudiant_id=None,
                        box_id=1,
                        date_field=date_obj,
                        creneau_id=creneau_id,
                        admin_field=True
                    )
                    Reservation.objects.create(
                        etudiant_id=None,
                        box_id=2,
                        date_field=date_obj,
                        creneau_id=creneau_id,
                        admin_field=True
                    )

        return redirect('accueilAdmin')
    else:
        return redirect('accueilAdmin')


def toggleBlockStudent(request, student_number):
    # Récupérer l'étudiant
    etudiant = get_object_or_404(Etudiant, num_etudiant=student_number)

    # Inverser le statut d'autorisation
    etudiant.autorise = not etudiant.autorise
    etudiant.save()

    # Rediriger vers le profil de l'étudiant
    return redirect('profilEtudiant', student_number=student_number)

def get_blocked_slots(request):
    date = request.GET.get('date')  # Date au format YYYY-MM-DD
    hour = request.GET.get('hour')  # Heure au format HH:MM

    if not date or not hour:
        return JsonResponse({'error': 'Date and hour are required'}, status=400)

    from datetime import datetime
    try:
        slot_datetime = datetime.strptime(f"{date} {hour}", "%Y-%m-%d %H:%M")
    except ValueError:
        return JsonResponse({'error': 'Invalid date or hour format'}, status=400)

    # Générer les sous-créneaux de 15 minutes pour cette heure : xx:00, xx:15, xx:30, xx:45
    sub_slots = [
        slot_datetime.replace(minute=0),
        slot_datetime.replace(minute=15),
        slot_datetime.replace(minute=30),
        slot_datetime.replace(minute=45),
    ]

    # Pour chaque sous-créneau, on vérifie s'il est bloqué pour les deux boxes.
    # Un sous-créneau est considéré bloqué si une réservation admin existe pour box 1 ET pour box 2.
    all_blocked = True
    for sub_slot in sub_slots:
        blocked_box1 = Reservation.objects.filter(
            date_field=date,
            creneau__heure_debut=sub_slot.time(),
            admin_field=True,
            box_id=1
        ).exists()
        blocked_box2 = Reservation.objects.filter(
            date_field=date,
            creneau__heure_debut=sub_slot.time(),
            admin_field=True,
            box_id=2
        ).exists()
        # Si au moins une box n'est pas bloquée pour ce sous-créneau, il est disponible.
        if not (blocked_box1 and blocked_box2):
            all_blocked = False
            break

    return JsonResponse({'all_blocked': all_blocked})

def cancelReservation(request, reservation_id):
    """
    Annule une réservation et redirige vers la page profilAdmin.
    """
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Supprimer la réservation
    reservation.delete()

    # Rediriger vers la page profilAdmin
    return redirect('profilAdmin')