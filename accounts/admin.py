from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'student_id', 'email', 'department', 'year_of_study', 'role', 'approval_status', 'is_active')
    list_filter = ('role', 'approval_status', 'department', 'year_of_study', 'is_active')
    search_fields = ('username', 'email', 'student_id', 'first_name', 'last_name')
    actions = ['approve_selected_students', 'reject_selected_students']

    fieldsets = UserAdmin.fieldsets + (
        ('College Academic Profile', {
            'fields': ('student_id', 'department', 'year_of_study', 'phone_number', 'profile_photo')
        }),
        ('Role & Verification', {
            'fields': ('role', 'approval_status', 'approved_by', 'approval_date', 'rejection_reason')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('College Profile', {
            'fields': ('email', 'student_id', 'department', 'year_of_study', 'role', 'approval_status')
        }),
    )

    @admin.action(description="Approve selected student accounts")
    def approve_selected_students(self, request, queryset):
        for user in queryset.filter(role='student'):
            user.approve(request.user)
        self.message_user(request, f"Successfully approved {queryset.count()} student accounts.")

    @admin.action(description="Reject selected student accounts")
    def reject_selected_students(self, request, queryset):
        for user in queryset.filter(role='student'):
            user.reject(request.user, reason="Administrative rejection via admin console.")
        self.message_user(request, f"Successfully rejected {queryset.count()} student accounts.")
