from django.urls import path
from . import views

app_name = 'voting'

urlpatterns = [
    path('ballot/<slug:slug>/', views.ballot_view, name='ballot'),
    path('ballot/<slug:slug>/confirm/', views.confirm_vote, name='confirm_vote'),
    path('ballot/<slug:slug>/submit/', views.submit_vote, name='submit_vote'),
    path('ballot/<slug:slug>/success/', views.vote_success, name='vote_success'),
    path('my-history/', views.my_votes_history, name='my_history'),
]
