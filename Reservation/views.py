from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.urls import reverse

# Create your views here.

def index(request):
    texte="<h2> Réservation de Box</h2> <br>Bienvenu.e sur le site de réservation de box \"silencieuses\"<br>"
    texte+=" <a href='/idEtudiant'><button>Etudiant</button></a> <br> <a href=''><button>Admin</button></a>"
    return HttpResponse(texte)

def idEtudiant(request):
    context = {
        'title': 'Identification Etudiant',
        'label': 'Numéro étudiant',
        'action_url': reverse('codeEtud')
    }
    return render(request,'formEtudiant.html',context)

def codeEtud(request):
    if(request.method=='POST'):
        NumEtud=request.POST.get('inputEtud')
        str(NumEtud)
        return HttpResponse("Num = "+NumEtud)
    #si code = 0000 :  return render(request,'accueilEtud.html',context)
    # donner l'id en plus

    else:
        context = {
            'title':'Identification Etudiant',
            'label':'Code de vérification',
            'action_url':reverse('accueilEtud'),
        }
        return render(request,'formEtudiant.html',context)
    
