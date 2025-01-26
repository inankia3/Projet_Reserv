from django.shortcuts import render, redirect,  get_object_or_404
from django.shortcuts import HttpResponse
from django.urls import reverse
from .models import *
from datetime import date, datetime, timedelta

# Create your views here.
NumEtud=''
idEtud=0
def index(request):
    return render(request,'index.html')


#--------------
#   Etudiant
#--------------

#vue avec le formulaire pour entrer le code étudiant
def idEtudiant(request):
    context = {
        'title': 'Identification Etudiant',
        'label': 'Numéro étudiant',
        'action_url': reverse('codeEtud')
    }
    return render(request,'formEtudiant.html',context)

#vue avec le formulaire pour entrer le code de vérification
# elle récupère le numéro étudiant
def codeEtud(request):
    if(request.method=='POST'):
        #on récupère et stock le numéro étudiant de l'utilisateur dans une variable de session
        request.session['NumEtud']=request.POST.get('inputEtud')
        str(NumEtud)
        context = {
            'title':'Identification Etudiant',
            'label':'Code de vérification',
            'action_url':reverse('accueilEtud'),
        }
        #envoi du code par mail ...
        return render(request,'formEtudiant.html',context)


    #empêche l'accès avec la barre de recherche
    else:
        return redirect('idEtudiant')

# vue d'accueil une fois connecté
# elle récupère et vérifie le code de vérification 
def accueilEtud(request):
    global NumEtud
    if(request.method=='POST'):
        code=request.POST.get('inputEtud')
        str(code)
        #Code erroné
        if(code!="0000"):
            context = {
                'title':'Erreur lors de la validation du code de vérification',
                'error':'Code de vérification incorrect',
                'action_url':reverse('index'),
            }
            return render(request,'erreur.html',context)
        #Code correct
        else:
            num_etud = request.session.get('NumEtud', '')
            request.session['is_admin']=False
            if not num_etud:
                # Si la session est vide ou a expiré
                context = {
                    'title': 'Erreur',
                    'error': 'Numéro étudiant introuvable en session.',
                    'action_url': reverse('index'),
                }
                return render(request, 'erreur.html', context)
             # Vérifier / créer l'étudiant dans la BDD
            idetud=Etudiant.objects.filter(num_etudiant=num_etud)
            if not idetud:
                etud=Etudiant(num_etudiant=num_etud)
                etud.save()
            global idEtud
            idEtud=idetud
            creneaux=Creneau.objects.all()
            reservations=Reservation.objects.all()
            context = {
                'action_url':reverse('calendrier1h_to_15'),
                'numero_etudiant':num_etud,
                'creneaux':creneaux,
                'reservations':reservations,
            }
            return render(request,'calendrier.html',context)

    else:
        context = {
            'title':'Identification Etudiant',
            'label':'Code de vérification',
            'action_url':reverse('accueilEtud'),
        }
        return render(request,'formEtudiant.html',context)

    
def vueCalendrier(request):
    """
    Affiche directement la page calendrier.html (sans demander le code).
    """
    # Contrôle d'accès minimal : vérifier que l'utilisateur est un étudiant connecté ou un admin
    if not request.session.get('NumEtud') and not request.session.get('is_admin'):
        # Ni étudiant (session) ni admin => on redirige vers un endroit logique
        return redirect('index')

    # Passer le numéro etudiant si c'est un étudiant
    num_etud = request.session.get('NumEtud')

    context = {
        'numero_etudiant': num_etud,
        'action_url': reverse('calendrier1h_to_15'),
    }
    return render(request, 'calendrier.html', context)

def calendrier1h_to_15(request):
    if request.method == 'POST':
        # Récupérer le créneau choisi (date + heure) depuis le champ hidden 'selected_slot'
        selected_slot = request.POST.get('selected_slot')  
        # Stocker en session (ou autrement) pour l'utiliser dans calendrier15
        if selected_slot:
            date_str, hour_str = selected_slot.split(' ')
            request.session['date_s'] = date_str
            request.session['heure_s'] = hour_str
        # Rediriger vers la vue calendrier15
        return redirect('calendrier15')
    else:
        # Si on arrive en GET, on renvoie par exemple vers la page calendrier
        return redirect('vueCalendrier')


def calendrier15(request):

    if request.method == 'POST' and not request.POST.get('selected_slot'):
        id_creneau=request.POST.get('selected_id')
        box=request.POST.get('selected_box')
        date=request.session.get('date_s')
        etudiant=request.session.get('NumEtud')

        idEtud=Etudiant.objects.get(num_etudiant=etudiant)
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        reservations_a_venir=Reservation.objects.filter(etudiant=idEtud).filter(date_field__gte=date_obj.today()).order_by('date_field')
        if reservations_a_venir.count() <2:
            idCreneau=Creneau.objects.get(id=id_creneau)
             # Création de la réservation
            reserv=Reservation.objects.create(
                etudiant=idEtud,
                box_id=int(box),
                creneau=idCreneau,
                date_field=date,   
                admin_field=False
             )
            reserv.save()
            # Redirection
        return redirect('vueCalendrier')  # ou accueilEtud, etc.
    else:
        date_str=request.session['date_s']
        heure_str=request.session['heure_s']
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        heure_obj = datetime.strptime(heure_str, "%H:%M").time()
        debut_heure = heure_obj
        fin_heure = (datetime.combine(datetime.min, heure_obj) + timedelta(hours=1)).time()
        creneaux_15_min_ids = Creneau.objects.filter(heure_debut__gte=debut_heure, heure_debut__lt=fin_heure).values_list('id', flat=True)

        creneaux_15_min = Creneau.objects.filter(heure_debut__gte=debut_heure, heure_debut__lt=fin_heure)
        reservations1 = Reservation.objects.filter(creneau__in=creneaux_15_min_ids, date_field=date_obj,box_id=1)
        reservations2 = Reservation.objects.filter(creneau__in=creneaux_15_min_ids, date_field=date_obj,box_id=2)


        # Prepare the formatted time strings
        time_slots = [{'id': creneau.id, 'heure_debut': creneau.heure_debut.strftime('%H:%M')} for creneau in creneaux_15_min]
        booked_slots1 = [reservation.creneau.heure_debut.strftime('%H:%M') for reservation in reservations1]
        booked_slots2 = [reservation.creneau.heure_debut.strftime('%H:%M') for reservation in reservations2]
        print(booked_slots2)
        print(booked_slots1)
        context = {
            'creneaux_15_min': creneaux_15_min,
            'date': date_obj,
            'heure': heure_str,
            'time_slots': time_slots,
            'booked_slots1': booked_slots1,
            'booked_slots2': booked_slots2,
        }
        return render(request, 'calendrier15.html', context)


# Nouvelle vue pour le profil de l'étudiant
def profilEtudiant(request,numero_etudiant):
    
    num_etud=request.session.get('NumEtud')
    idEtud=Etudiant.objects.filter(num_etudiant=num_etud).values_list('id', flat=True)
    etud=Etudiant.objects.get(num_etudiant=num_etud)
    date_=date.today()
    if not (request.session.get('is_admin')) and (num_etud != numero_etudiant):
        return render(request, 'erreur.html', {
            'title': 'Accès refusé',
            'error': "Vous n'êtes pas autorisé à consulter ce profil.",
            'action_url': reverse('index'),  
        })


    #__gt signifie plus grand que : greater than or equal to
    reservations_a_venir=Reservation.objects.filter(etudiant__in=idEtud).filter(date_field__gte=date_).order_by('date_field')
 
    reservations_passees=Reservation.objects.filter(etudiant__in=idEtud).filter(date_field__lt=date_).order_by('-date_field')


    context = {
        'title': 'Profil Etudiant',
        'etudiant':etud,
        'reservations_a_venir': reservations_a_venir,
        'reservations_passees': reservations_passees,
        'numero_etudiant': num_etud,
        'is_admin':request.session.get('is_admin'),
    }
    return render(request, 'profilEtudiant.html', context)


#--------------
#    ADMIN
#--------------

# Vue pour la connexion de l'admin
def adminLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        identifiant=Admin.objects.filter(identifiant=username,mdp=password)
        if identifiant:
            # Redirection vers le tableau de bord de l'admin
            request.session['is_admin']=True
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
    if not request.session.get('is_admin',False):
        return redirect('adminLogin')
    context = {
        'title': 'Gestion des réservations - Admin',
        #'action_url': reverse('accueilAdmin'),  # L'action du formulaire pointe vers la même vue
    }
    return render(request, 'calendrierAdmin.html', context)

def profilAdmin(request):
    etudiants = Etudiant.objects.all()
    reservations_jour = Reservation.objects.filter(date_field=date.today()).filter(admin_field=0)
    reservations_a_venir = Reservation.objects.filter(date_field__gt=date.today()).filter(admin_field=0)

    context = {
        'title': 'Profil Admin',
        'etudiants': etudiants,
        'reservations_jour': reservations_jour,
        'reservations_a_venir':reservations_a_venir,
    }
    return render(request, 'profilAdmin.html', context)

def toggleBlockStudent(request, numero_etudiant):
    etudiant=Etudiant.objects.get(num_etudiant=numero_etudiant)
    if not etudiant:
        return HttpResponse("Étudiant non trouvé", status=404)

    # Inverser l'état de blocage de l'étudiant
    if(etudiant.autorise==1):
        etudiant.autorise=0
    else:
        etudiant.autorise=1
    etudiant.save()
    # Rediriger vers le profil de l'étudiant
    return redirect('profilEtudiant', numero_etudiant)



def blockSlotsAdmin(request):
    print('test')
    if request.method == 'POST':
        selected_hours = request.POST.get('selected_hours', '').strip()
        which_box = request.POST.get('which_box', '').strip()  # "1","2","1-2"
        print('test1')
        if not selected_hours:
            print('test2')
            return redirect('accueilAdmin')

        list_slots = selected_hours.split(',')  # ex. ["2025-02-10 09:00", ...]
        for slot in list_slots:
            slot = slot.strip()
            date_str, hour_str = slot.split(' ')
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            heure= datetime.strptime(hour_str,"%H:%M").time()
            print('test3')

            # On trouve le premier creneau 15 min => hour_int:00 -> hour_int:15
            heure_debut = heure
            heure_fin = (datetime.combine(date_obj, heure_debut)
                         + timedelta(minutes=15)).time()
            first_creneau = Creneau.objects.filter(
                heure_debut=heure_debut,
                heure_fin=heure_fin
            ).first()
            if not first_creneau:
                # ne pas planter, on skip
                continue

            # Vérifier si le créneau est déjà bloqué
            existing_reservation = Reservation.objects.filter(
                date_field=date_obj,
                creneau_id=first_creneau.id,
                admin_field=True
            ).first()

            if existing_reservation:
                # Débloquer le créneau (supprimer la réservation)
                existing_reservation.delete()
            else:
                # On crée 4 ou 8 reservations
                for offset in range(4):
                    id_creneau = first_creneau.id + offset
                    if which_box == "1":
                        reserv=Reservation.objects.create(
                            etudiant_id=None,
                            box_id=1,
                            date_field=date_obj,
                            creneau_id=id_creneau,
                            admin_field=True
                        )
                        reserv.save()
                    elif which_box == "2":
                        reserv=Reservation.objects.create(
                            etudiant_id=None,
                            box_id=2,
                            date_field=date_obj,
                            creneau_id=id_creneau,
                            admin_field=True
                        )
                        reserv.save()

                    elif which_box == "1-2":
                        # 2 reservations (box1 + box2)
                        reserv=Reservation.objects.create(
                            etudiant_id=None,
                            box_id=1,
                            date_field=date_obj,
                            creneau_id=id_creneau,
                            admin_field=True
                        )
                        reserv.save()

                        reserv=Reservation.objects.create(
                            etudiant_id=None,
                            box_id=2,
                            date_field=date_obj,
                            creneau_id=id_creneau,
                            admin_field=True
                        )
                        reserv.save()


        return redirect('accueilAdmin')
    else:
        return redirect('accueilAdmin')



def cancelReservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    etudiant = reservation.etudiant

    # Décrémenter le compteur de réservations à venir
    if etudiant.reservations_a_venir > 0:
        etudiant.reservations_a_venir -= 1
        etudiant.save()

    reservation.delete()
    return redirect('profilEtudiant', student_number=etudiant.num_etudiant)