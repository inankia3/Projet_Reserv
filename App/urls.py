from django.contrib import admin
from django.urls import path
from Reservation import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),

    # Parcours étudiant
    path('idEtudiant/', views.idEtudiant, name='idEtudiant'),
    path('envoyer_code_verification/',views.envoyer_code_verification, name='envoyer_code_verification'),
    path('codeEtud/', views.codeEtud, name='codeEtud'),
    path('accueilEtud/', views.accueilEtud, name='accueilEtud'),
    path('vueCalendrier/', views.vueCalendrier, name='vueCalendrier'),
    path('calendrier15/', views.calendrier15, name='calendrier15'),
    path('calendrier1h_to_15/', views.calendrier1h_to_15, name='calendrier1h_to_15'),
    path('profilEtudiant/<str:student_number>/', views.profilEtudiant, name='profilEtudiant'),

    # Parcours admin
    path('adminLogin/', views.adminLogin, name='adminLogin'),
    path('accueilAdmin/', views.accueilAdmin, name='accueilAdmin'),
    path('profilAdmin/', views.profilAdmin, name='profilAdmin'),
    path('toggleBlockStudent/<str:student_number>/', views.toggleBlockStudent, name='toggleBlockStudent'),
    path('blockSlotsAdmin/', views.blockSlotsAdmin, name='blockSlotsAdmin'),
    path('get_blocked_slots/', views.get_blocked_slots, name='get_blocked_slots'),
    path('cancelReservation/<int:reservation_id>/', views.cancelReservation, name='cancelReservation'),
]
