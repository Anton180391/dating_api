from django.contrib import admin

from .models import DateInvitation, Interaction, ProfileView


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ("id", "from_user", "to_user", "type", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("from_user__email", "to_user__email")
    date_hierarchy = "created_at"


@admin.register(ProfileView)
class ProfileViewAdmin(admin.ModelAdmin):
    list_display = ("id", "viewer", "viewed", "viewed_at")
    list_filter = ("viewed_at",)
    search_fields = ("viewer__email", "viewed__email")
    date_hierarchy = "viewed_at"


@admin.register(DateInvitation)
class DateInvitationAdmin(admin.ModelAdmin):
    list_display = ("id", "from_user", "to_user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("from_user__email", "to_user__email")
    date_hierarchy = "created_at"
