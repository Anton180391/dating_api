from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Hobby, UserPhoto
from .serializers import (
    HobbySerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserPhotoSerializer,
    UserRegisterSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для пользователей.
    """

    queryset = User.objects.select_related("main_photo").prefetch_related(
        "hobbies", "photos"
    )
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["gender", "city", "status"]
    search_fields = ["first_name", "last_name", "email", "city"]
    ordering_fields = ["age", "created_at", "likes_count"]

    def get_queryset(self):
        """Оптимизация запросов."""
        return User.objects.select_related("main_photo").prefetch_related(
            "hobbies", "photos"
        )


class HobbyViewSet(viewsets.ModelViewSet):
    """Справочник увлечений."""

    queryset = Hobby.objects.all()
    serializer_class = HobbySerializer
    permission_classes = [IsAuthenticated]


class UserPhotoViewSet(viewsets.ModelViewSet):
    """Фотографии пользователя."""

    queryset = UserPhoto.objects.all()
    serializer_class = UserPhotoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserPhoto.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
