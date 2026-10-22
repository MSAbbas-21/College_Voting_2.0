from django.contrib import admin
from .models import Candidate


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'election', 'student_id', 'department', 'vote_count', 'vote_percentage')
    list_filter = ('election', 'position', 'department')
    search_fields = ('name', 'student_id', 'manifesto')
