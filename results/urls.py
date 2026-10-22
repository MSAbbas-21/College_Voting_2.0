from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    path('', views.results_index, name='results_list'),
    path('<slug:slug>/', views.election_result_detail, name='election_result'),
    path('<slug:slug>/print/', views.print_result_report, name='print_result'),
]
