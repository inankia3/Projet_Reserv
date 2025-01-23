"""
URL configuration for App project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Reservation import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),
    path('idEtudiant/',views.idEtudiant,name='idEtudiant'),
    path('codeEtud/',views.codeEtud,name='codeEtud'),
    path('accueilEtud/',views.accueilEtud,name='accueilEtud'),
    path('calendrier15/',views.calendrier15,name='calendrier15'),
    path('profilEtudiant/',views.profilEtudiant,name='profilEtudiant'),
    path('adminLogin/',views.adminLogin,name='adminLogin'),

    path('accueilAdmin/',views.accueilAdmin,name='accueilAdmin'),

    path('Reservation/',views.index,name='index')
]
