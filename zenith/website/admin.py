from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Admission, Contact, Tutor,Student
from django.contrib.auth import get_user_model

class CustomUserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('User Role', {'fields': ('role',)}),
    )

class TutorAdmin(admin.ModelAdmin):
    list_display = ['Name', 'Subject', 'Email', 'PhoneNumber', 'UserId']
    search_fields = ['UserId__username', 'Subject']

class StudentAdmin(admin.ModelAdmin):
    list_display = ['Name', 'Class', 'Group', 'Email']
    search_fields = ['Name', 'Email']

User=get_user_model()
admin.site.register(User, CustomUserAdmin)
admin.site.register(Tutor, TutorAdmin)
admin.site.register(Admission)
admin.site.register(Contact)
admin.site.register(Student, StudentAdmin)

# Register your models here.
