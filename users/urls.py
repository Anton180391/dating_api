from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import HobbyViewSet, UserPhotoViewSet, UserViewSet

app_name = "users"

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"hobbies", HobbyViewSet, basename="hobby")
router.register(r"photos", UserPhotoViewSet, basename="photo")

urlpatterns = [
    path("", include(router.urls)),
]
