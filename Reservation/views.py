from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.urls import reverse

# Create your views here.
NumEtud=''
admin_username = 'admin'
admin_password = 'admin123'  # Mot de passe simple pour l'exemple, à ne pas utiliser en production

def index(request):
    texte="<h2> Réservation de Box</h2> <br>Bienvenu.e sur le site de réservation de box \"silencieuses\"<br>"
    texte+=" <a href='/idEtudiant'><button>Etudiant</button></a> <br> <a href='/adminLogin'><button>Admin</button></a>"
    return HttpResponse(texte)

# Vue pour la connexion de l'admin
def adminLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == admin_username and password == admin_password:
            # Redirection vers le tableau de bord de l'admin
            return redirect('adminDashboard')
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
            context = {
                'action_url':reverse('calendrier15'),
            }
            #ajout de l'étudiant dans la base de donnée
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
        creneau=request.POST.get('selected_slot')
        #vérifie le code de vérification entré
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
