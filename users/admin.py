from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Hobby, User, UserPhoto


class UserPhotoInline(admin.TabularInline):
    model = UserPhoto
    extra = 1


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "full_name", "gender", "age", "city", "status")
    list_filter = ("gender", "status", "city")
    search_fields = ("email", "first_name", "last_name", "city")
    inlines = [UserPhotoInline]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личная информация",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "patronymic",
                    "gender",
                    "age",
                    "city",
                ),
            },
        ),
        (
            "Профиль",
            {
                "fields": ("hobbies", "status", "main_photo", "likes_count"),
            },
        ),
        (
            "Приватность",
            {
                "fields": ("show_age", "show_city", "show_hobbies", "show_online"),
            },
        ),
        (
            "Права",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Даты",
            {
                "fields": ("last_login", "date_joined", "created_at", "updated_at"),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at", "likes_count")


@admin.register(Hobby)
class HobbyAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(UserPhoto)
class UserPhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "order", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__email",)
