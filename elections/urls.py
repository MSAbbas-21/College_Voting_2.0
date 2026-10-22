from django.urls import path
from . import views

app_name = 'elections'

urlpatterns = [
    path('', views.public_election_list, name='election_list'),
    path('<slug:slug>/', views.public_election_detail, name='election_detail'),
]
