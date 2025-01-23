from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import HttpResponse
from django.urls import reverse
from .models import *
'''
from django.http import JsonResponse

from django.core.serializers.json import DjangoJSONEncoder
import json
'''
# Create your views here.
NumEtud=''

# Données fictives pour l'exemple
admin_username = 'admin'
admin_password = 'admin123'  # Mot de passe simple pour l'exemple, à ne pas 
Admin_=False

students = [
    {'student_number': 'E12345', 'name': 'Jean Dupont', 'blocked': False},
    {'student_number': 'E67890', 'name': 'Marie Curie', 'blocked': True},
]

reservations_today = [
    {'student_number': 'E12345', 'box_number': 'Box 1', 'time': '09:00 - 10:00'},
    {'student_number': 'E67890', 'box_number': 'Box 2', 'time': '10:00 - 11:00'},
]

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
            context = {
                'action_url':reverse('calendrier15'),
            }
            return render(request,'calendrier.html',context)
            '''            #MODIF
            creneaux = Creneau.objects.all()
            grouped_creneaux = {}

        for creneau in creneaux:
            heure_debut = creneau.heure_debut.strftime('%H:%M:00')
            heure_fin = creneau.heure_fin.strftime('%H:%M:00')
            if heure_debut.endswith(':00:00'):
                grouped_creneaux[heure_debut] = []

            grouped_creneaux[heure_debut].append({
                'heure_debut': heure_debut,
                'heure_fin':creneau.heure_debut.strftime('%H:00:00')
            })

            grouped_creneaux_json = json.dumps(grouped_creneaux, cls=DjangoJSONEncoder)
            print("test1",grouped_creneaux)

            print("test",grouped_creneaux_json)
            context = {
                'action_url':reverse('calendrier15'),
                'grouped_creneaux':  grouped_creneaux_json,
            }
            #return render(request, 'calendrier.html', context)
            
            #ajout de l'étudiant dans la base de donnée'''

    else:
        context = {
            'title':'Identification Etudiant',
            'label':'Code de vérification',
            'action_url':reverse('accueilEtud'),
        }
        return render(request,'formEtudiant.html',context)

def calendrier15(request):
    if(request.method=='POST'):
        creneau=request.POST.get('selected_slot')
        #context = {
        #    'action_url':reverse('validation'),
        #}
        #return render(request,'calendrier15.html',context)
        return render(request,'calendrier15.html')


# Nouvelle vue pour le profil de l'étudiant
def profilEtudiant(request):
    reservations_a_venir = [ #à modifier pour récupérer les données de la base de données
        {'date': '2025-01-24', 'creneau': '09:00 - 09:15'},
        {'date': '2025-01-25', 'creneau': '10:15 - 10:30'}
    ]
    reservations_passees = [ #à modifier pour récupérer les données de la base de données
        {'date': '2025-01-20', 'creneau': '11:00 - 11:15'},
        {'date': '2025-01-21', 'creneau': '12:45 - 13:00'}
    ]

    context = {
        'title': 'Profil Etudiant',
        'reservations_a_venir': reservations_a_venir,
        'reservations_passees': reservations_passees,
        'student_number': NumEtud
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
    context = {
        'title': 'Profil Admin',
        'students': students,
        'reservations_today': reservations_today,
    }
    return render(request, 'profilAdmin.html', context)

def toggleBlockStudent(request, student_number):
    # Trouver l'étudiant dans la liste simulée
    student = next((s for s in students if s['student_number'] == student_number), None)
    if not student:
        return HttpResponse("Étudiant non trouvé", status=404)

    # Inverser l'état de blocage de l'étudiant
    student['blocked'] = not student['blocked']

    # Rediriger vers le profil de l'étudiant
    return redirect('profilEtudiant', student_number=student_number)