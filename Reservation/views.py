from django.shortcuts import render, redirect,  get_object_or_404
from django.shortcuts import HttpResponse
from django.urls import reverse
from .models import *
from datetime import date, datetime, timedelta

# Create your views here.
NumEtud=''
idEtud=0
def index(request):
    texte = """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap');

            body {
                font-family: 'Roboto', sans-serif;
                background-color: #f4f4f4;
                color: #333;
                margin: 0;
                padding: 20px;
            }
            header {
                text-align: center;
                padding: 10px 0;
            }
        h1 {

            font-size: 2em; 
            margin: 0;
            padding: 10px 0;
        }
            h2 {
                color: #BF1E2E; /* Rouge inspiré par le logo */
                font-family: 'Roboto', sans-serif;
            }
            a {
                text-decoration: none;
            }
            button {
                background-color: #BF1E2E; /* Rouge inspiré par le logo */
                color: white;
                border: none;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 10px 2px;
                cursor: pointer;
                border-radius: 4px;
            }
            button:hover {
                background-color: #9B1623; /* Rouge plus foncé pour l'effet hover */
            }
        </style>
        <header>
            <h1>Réservation de Box</h1>
        </header>
        <h2>Bienvenu.e sur le site de réservation de box "silencieuses"</h2>
        <br>
        <a href='/idEtudiant'><button>Etudiant</button></a>
        <br>
        <a href='/adminLogin'><button>Admin</button></a>
    """
    return HttpResponse(texte)


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
                'action_url':reverse('calendrier15'),
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
        'action_url': reverse('calendrier15'),
    }
    return render(request, 'calendrier.html', context)


def calendrier15(request):

    if request.method == 'POST':
        creneau_str = request.POST.get('selected_slot')
        date_str, heure_str = creneau_str.split()
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        heure_obj = datetime.strptime(heure_str, "%H:%M").time()
        print('creneau', creneau_str)
        print(f"Date : {date_obj}")
        print(f"Heure : {heure_obj}")
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
    global idEtud
    num_etud=request.session.get('NumEtud')
    date_=date.today()
    if not (request.session.get('is_admin') or num_etud == numero_etudiant):
        return render(request, 'erreur.html', {
            'title': 'Accès refusé',
            'error': "Vous n'êtes pas autorisé à consulter ce profil.",
            'action_url': reverse('index'),  
        })


    #__gt signifie plus grand que : greater than or equal to
    reservations_a_venir=Reservation.objects.filter(etudiant__in=idEtud).filter(date_field__gte=date_).order_by('date_field')
    print(f"a venir :{list(reservations_a_venir)}")
 
    reservations_passees=Reservation.objects.filter(etudiant__in=idEtud).filter(date_field__lt=date_).order_by('-date_field')
    print(f"passee :{list(reservations_passees)}")
    

    context = {
        'title': 'Profil Etudiant',
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
        'action_url': reverse('accueilAdmin'),  # L'action du formulaire pointe vers la même vue
    }
    return render(request, 'calendrierAdmin.html', context)

def profilAdmin(request):
    etudiants = Etudiant.objects.all()
    reservations_jour = Reservation.objects.filter(date_field=date.today())

    context = {
        'title': 'Profil Admin',
        'etudiants': etudiants,
        'reservations_jour': reservations_jour,
    }
    return render(request, 'profilAdmin.html', context)

def toggleBlockStudent(request, num_etud):
    etudiant=Etudiant.objects.filter(num_etudiant=num_etud)
    if not etudiant:
        return HttpResponse("Étudiant non trouvé", status=404)

    # Inverser l'état de blocage de l'étudiant
    etudiant['autorise'] = not etudiant['autorise']

    # Rediriger vers le profil de l'étudiant
    return redirect('profilEtudiant', num_etudiant=num_etud)




