from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.urls import reverse

# Create your views here.
NumEtud=''
def index(request):
    texte="<h2> Réservation de Box</h2> <br>Bienvenu.e sur le site de réservation de box \"silencieuses\"<br>"
    texte+=" <a href='/idEtudiant'><button>Etudiant</button></a> <br> <a href=''><button>Admin</button></a>"
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
    #if(request.method=='POST'):
    #on récupère et stock le numéro étudiant de l'utilisateur
    global NumEtud
    NumEtud=request.POST.get('inputEtud')
    str(NumEtud)

    #si code = 0000 :  return render(request,'accueilEtud.html',context)
    # donner l'id en plus

    #else:
    context = {
        'title':'Identification Etudiant',
        'label':'Code de vérification',
        'action_url':reverse('accueilEtud'),
    }
    return render(request,'formEtudiant.html',context)

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
            return HttpResponse("Bienvenu "+NumEtud)

    #si code = 0000 :  return render(request,'accueilEtud.html',context)
    # donner l'id en plus

    else:
        context = {
            'title':'Identification Etudiant',
            'label':'Code de vérification',
            'action_url':reverse('accueilEtud'),
        }
        return render(request,'formEtudiant.html',context)
    