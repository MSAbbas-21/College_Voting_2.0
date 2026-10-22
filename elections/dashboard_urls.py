from django.urls import path
from . import admin_views

app_name = 'dashboard'

urlpatterns = [
    # Admin Dashboard Overview
    path('', admin_views.admin_dashboard, name='admin_dashboard'),
    
    # Student Management
    path('students/', admin_views.students_list, name='students_list'),
    path('students/<int:user_id>/', admin_views.student_detail, name='student_detail'),
    path('students/<int:user_id>/approve/', admin_views.student_approve, name='student_approve'),
    path('students/<int:user_id>/reject/', admin_views.student_reject, name='student_reject'),
    path('students/<int:user_id>/toggle-active/', admin_views.student_toggle_active, name='student_toggle_active'),
    
    # Election Management
    path('elections/', admin_views.elections_list, name='elections_list'),
    path('elections/create/', admin_views.election_create, name='election_create'),
    path('elections/<int:pk>/', admin_views.election_detail_admin, name='election_detail'),
    path('elections/<int:pk>/edit/', admin_views.election_edit, name='election_edit'),
    path('elections/<int:pk>/delete/', admin_views.election_delete, name='election_delete'),
    path('elections/<int:pk>/toggle-status/', admin_views.election_toggle_status, name='election_toggle_status'),
    path('elections/<int:pk>/toggle-publish/', admin_views.election_toggle_publish, name='election_toggle_publish'),
    
    # Candidate Management
    path('candidates/', admin_views.candidates_list, name='candidates_list'),
    path('candidates/create/', admin_views.candidate_create, name='candidate_create'),
    path('candidates/<int:pk>/edit/', admin_views.candidate_edit, name='candidate_edit'),
    path('candidates/<int:pk>/delete/', admin_views.candidate_delete, name='candidate_delete'),
    
    # System Analytics
    path('analytics/', admin_views.analytics_summary, name='analytics'),
]
