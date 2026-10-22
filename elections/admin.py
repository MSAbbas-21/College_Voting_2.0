from django.contrib import admin
from .models import Election


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_date', 'end_date', 'is_published', 'candidate_count', 'total_votes_count')
    list_filter = ('status', 'is_published', 'start_date')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    actions = ['open_voting', 'close_voting', 'publish_results', 'unpublish_results']

    @admin.action(description="Open voting for selected elections")
    def open_voting(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, "Selected elections are now Active.")

    @admin.action(description="Close voting for selected elections")
    def close_voting(self, request, queryset):
        queryset.update(status='closed')
        self.message_user(request, "Selected elections are now Closed.")

    @admin.action(description="Publish results for selected elections")
    def publish_results(self, request, queryset):
        queryset.update(is_published=True)
        self.message_user(request, "Selected election results have been Published.")

    @admin.action(description="Unpublish results for selected elections")
    def unpublish_results(self, request, queryset):
        queryset.update(is_published=False)
        self.message_user(request, "Selected election results have been Hidden.")
