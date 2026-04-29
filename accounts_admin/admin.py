from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import ManagedUser


@admin.register(ManagedUser)
class ManagedUserAdmin(DjangoUserAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "course",
        "enrollment_year",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    list_filter = (
        "role",
        "course",
        "enrollment_year",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("College Hub", {"fields": ("role", "course", "enrollment_year", "about_me", "avatar")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("College Hub", {"fields": ("role", "course", "enrollment_year", "about_me", "avatar")}),
    )
