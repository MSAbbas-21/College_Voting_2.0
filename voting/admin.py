from django.contrib import admin
from .models import VoterParticipation, Vote


@admin.register(VoterParticipation)
class VoterParticipationAdmin(admin.ModelAdmin):
    list_display = ('student', 'election', 'receipt_code', 'voted_at')
    list_filter = ('election', 'voted_at')
    search_fields = ('student__username', 'student__student_id', 'student__email', 'receipt_code')
    readonly_fields = ('student', 'election', 'receipt_code', 'voted_at')

    def has_add_permission(self, request):
        return False  # Participation can only be cast through ballot


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    # Notice: No student field displayed, preserving voter secrecy
    list_display = ('election', 'candidate', 'cast_at')
    list_filter = ('election', 'candidate')
    search_fields = ('election__title', 'candidate__name')
    readonly_fields = ('election', 'candidate', 'cast_at')

    def has_add_permission(self, request):
        return False  # Votes are only cast via voting booth
