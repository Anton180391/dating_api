from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DateInvitationViewSet, InteractionViewSet, ProfileViewViewSet

app_name = "interactions"

router = DefaultRouter()
router.register(r"interactions", InteractionViewSet, basename="interaction")
router.register(r"views", ProfileViewViewSet, basename="view")
router.register(r"invitations", DateInvitationViewSet, basename="invitation")

urlpatterns = [
    path("", include(router.urls)),
]
