from django.shortcuts import render, redirect,  get_object_or_404
from django.shortcuts import HttpResponse
from django.urls import reverse
from .models import *
from datetime import date, datetime, timedelta
'''
from django.http import JsonResponse

from django.core.serializers.json import DjangoJSONEncoder
import json
'''
# Create your views here.
NumEtud=''
admin_username = 'admin'
admin_password = 'admin123'  # Mot de passe simple pour l'exemple, à ne pas 
Admin_=False
idEtud=0
def index(request):
   texte="<h2> Réservation de Box</h2> <br>Bienvenu.e sur le site de réservation de box \"silencieuses\"<br>"
   texte+=" <a href='/idEtudiant'><button>Etudiant</button></a> <br> <a href='/adminLogin'><button>Admin</button></a>"
   return HttpResponse(texte)

#vue avec le formulaire pour entrer le code étudiant
def idEtudiant(request):
    context = {
        'title': 'Identification Etudiant',
        'label': 'Numéro étudiant',
        'action_url': reverse('codeEtud')
    }
    return render(request,'formEtudiant.html',context)

#vue avec le formulaire pour entrer le code étudiant
def codeEtud(request):
    if(request.method=='POST'):
    #on récupère et stock le numéro étudiant de l'utilisateur
        global NumEtud
        NumEtud=request.POST.get('inputEtud')
        str(NumEtud)
        context = {
            'title':'Identification Etudiant',
            'label':'Code de vérification',
            'action_url':reverse('accueilEtud'),
        }
        return render(request,'formEtudiant.html',context)

    #si code = 0000 :  return render(request,'accueilEtud.html',context)
    # donner l'id en plus

    #else:

# vue d'accueil une fois connecté
def accueilEtud(request):
    global NumEtud
    if(request.method=='POST'):
        code=request.POST.get('inputEtud')
        str(code)
        #vérifie le code de vérification entré
        if(code!="0000"):
            context = {
                'title':'Erreur lors de la validation du code de vérification',
                'error':'Code de vérification incorrect',
                'action_url':reverse('index'),
            }
            return render(request,'erreur.html',context)
        else:
            idetud=Etudiant.objects.filter(num_etudiant=NumEtud)
            if not idetud:
                etud=Etudiant(num_etudiant=NumEtud)
                etud.save()
            global idEtud
            idEtud=idetud
            creneaux=Creneau.objects.all()
            reservations=Reservation.objects.all()
            context = {
                'action_url':reverse('calendrier15'),
                'student_number':NumEtud,
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


def calendrier15(request):
    if(request.method=='POST'):
        creneau_str=request.POST.get('selected_slot')
        date_str,heure_str=creneau_str.split()
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        heure_obj = datetime.strptime(heure_str, "%H:%M").time()
        print('creneau',creneau_str)
        print(f"Date : {date_obj}")
        print(f"Heure : {heure_obj}")
        debut_heure = heure_obj
        fin_heure = (datetime.combine(datetime.min, heure_obj) + timedelta(hours=1)).time()


        creneaux_15_min_ids = Creneau.objects.filter(heure_debut__gte=debut_heure, heure_debut__lt=fin_heure).values_list('id', flat=True)
        creneaux_15 = {Creneau.objects.get(id=creneau_id) for creneau_id in creneaux_15_min_ids}
        reservations = Reservation.objects.filter(creneau__in=creneaux_15_min_ids, date_field=date_obj)
        time_slots = [Creneau.objects.get(id=creneau_id).heure_debut.strftime('%H:%M') for creneau_id in creneaux_15_min_ids]
        booked_slots = [reservation.creneau.heure_debut.strftime('%H:%M') for reservation in reservations]

        context = {
            'creneaux_15_min': creneaux_15_min_ids,
            'date': date_obj,
            'heure': heure_str,
            'time_slots': time_slots,
            'booked_slots': booked_slots,
         }
        return render(request, 'calendrier15.html', context)


# Nouvelle vue pour le profil de l'étudiant
def profilEtudiant(request):
    global idEtud
    global NumEtud
    date_=date.today()
    #__gt signifie plus grand que : greater than or equal to
    reservations_a_venir=Reservation.objects.filter(etudiant__in=idEtud).filter(date_field__gte=date_).order_by('date_field')
    print(f"a venir :{list(reservations_a_venir)}")
 
    reservations_passees=Reservation.objects.filter(etudiant__in=idEtud).filter(date_field__lt=date_).order_by('-date_field')
    print(f"passee :{list(reservations_passees)}")

    context = {
        'title': 'Profil Etudiant',
        'reservations_a_venir': reservations_a_venir,
        'reservations_passees': reservations_passees,
        'student_number': NumEtud,
    }
    return render(request, 'profilEtudiant.html', context)

# Vue pour la connexion de l'admin
def adminLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        identifiant=Admin.objects.filter(identifiant=username,mdp=password)
        if identifiant:
            # Redirection vers le tableau de bord de l'admin
            global Admin_
            Admin_=True
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
    '''if request.method == 'POST':
        # Gérer la soumission du formulaire pour bloquer un créneau
        selected_slot = request.POST.get('selected_slot')
        if selected_slot:
            date, time = selected_slot.split(' ')
            blocked_slots.append({'date': date, 'time': time})
    '''
    context = {
        'title': 'Gestion des réservations - Admin',
        #'reservations': reservations,
        #'blocked_slots': blocked_slots,
        'action_url': reverse('accueilAdmin'),  # L'action du formulaire pointe vers la même vue
    }
    return render(request, 'calendrierAdmin.html', context)

def profilAdmin(request):
    students=Etudiant.objects.all()
    reservation_jour=Reservation.objects.filter(date_field=date.today())
    context = {
        'title': 'Profil Admin',
        'students': students,
        'reservations_today': reservation_jour,
    }
    return render(request, 'profilAdmin.html', context)


def toggleBlockStudent(request, student_number):
    students=Etudiant.objects.all()
    # Trouver l'étudiant dans la liste simulée
    student = next((s for s in students if s['num_etudiant'] == student_number), None)
    if not student:
        return HttpResponse("Étudiant non trouvé", status=404)

    # Inverser l'état de blocage de l'étudiant
    #student['blocked'] = not student['blocked']

    # Rediriger vers le profil de l'étudiant
    return redirect('profilEtudiant', student_number=student_number)




