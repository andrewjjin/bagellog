from django.urls import path
from . import views

urlpatterns = [
    path('tournaments/', views.tournament_list, name='tournament_list'),
    path('tournaments/create/', views.create_tournament, name='create_tournament'),
    path('tournaments/<int:tournament_id>/', views.tournament_detail, name='tournament_detail'),
    path('tournaments/<int:tournament_id>/register/', views.register_tournament, name='register_tournament'),
    path('tournaments/<int:tournament_id>/save-bracket/', views.save_bracket, name='save_bracket'),
    path('tournaments/<int:tournament_id>/load-bracket/', views.load_bracket, name='load_bracket'),
    path('my-brackets/', views.user_brackets, name='user_brackets'),
    path('api/tournaments/<int:tournament_id>/participants/', views.tournament_participants_api, name='tournament_participants_api'),
]
