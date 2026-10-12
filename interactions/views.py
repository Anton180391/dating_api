from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.serializers import UserListSerializer

from .models import DateInvitation, Interaction, ProfileView
from .serializers import (
    DateInvitationSerializer,
    InteractionSerializer,
    ProfileViewSerializer,
)

User = get_user_model()


class InteractionViewSet(viewsets.ModelViewSet):
    """Лайки и дизлайки."""

    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["type", "to_user"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        """Оптимизация: select_related для from_user и to_user."""
        return Interaction.objects.select_related("from_user", "to_user").filter(
            from_user=self.request.user
        )

    def perform_create(self, serializer):
        interaction = serializer.save(from_user=self.request.user)

        # Обновляем счётчик лайков у получателя
        if interaction.type == Interaction.Type.LIKE:
            User.objects.filter(pk=interaction.to_user.pk).update(
                likes_count=models.F("likes_count") + 1
            )

    @action(detail=False, methods=["get"], url_path="liked-me")
    def liked_me(self, request):
        """Кто лайкнул меня."""
        likers = (
            User.objects.select_related("main_photo")
            .prefetch_related("hobbies", "photos")
            .filter(
                interactions_sent__to_user=request.user,
                interactions_sent__type=Interaction.Type.LIKE,
            )
            .distinct()
        )
        serializer = UserListSerializer(likers, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="my-likes")
    def my_likes(self, request):
        """Кого лайкнул я."""
        liked = (
            User.objects.select_related("main_photo")
            .prefetch_related("hobbies", "photos")
            .filter(
                interactions_received__from_user=request.user,
                interactions_received__type=Interaction.Type.LIKE,
            )
            .distinct()
        )
        serializer = UserListSerializer(liked, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="my-dislikes")
    def my_dislikes(self, request):
        """Кого я дизлайкнул."""
        disliked = (
            User.objects.select_related("main_photo")
            .prefetch_related("hobbies", "photos")
            .filter(
                interactions_received__from_user=request.user,
                interactions_received__type=Interaction.Type.DISLIKE,
            )
            .distinct()
        )
        serializer = UserListSerializer(
            disliked, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="mutual")
    def mutual_likes(self, request):
        """Взаимные лайки."""
        # Кого я лайкнул
        my_likes = Interaction.objects.filter(
            from_user=request.user,
            type=Interaction.Type.LIKE,
        ).values_list("to_user_id", flat=True)

        # Кто лайкнул меня в ответ
        mutual = (
            User.objects.select_related("main_photo")
            .prefetch_related("hobbies", "photos")
            .filter(
                id__in=my_likes,
                interactions_sent__to_user=request.user,
                interactions_sent__type=Interaction.Type.LIKE,
            )
            .distinct()
        )

        serializer = UserListSerializer(mutual, many=True, context={"request": request})
        return Response(serializer.data)


class ProfileViewViewSet(viewsets.ModelViewSet):
    """История просмотров."""

    serializer_class = ProfileViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Оптимизация: select_related для viewer и viewed."""
        return ProfileView.objects.select_related("viewer", "viewed").filter(
            viewer=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(viewer=self.request.user)

    @action(detail=False, methods=["get"], url_path="who-viewed-me")
    def who_viewed_me(self, request):
        """Кто смотрел мой профиль."""
        viewers = (
            User.objects.select_related("main_photo")
            .prefetch_related("hobbies", "photos")
            .filter(
                views_made__viewed=request.user,
            )
            .distinct()
        )
        serializer = UserListSerializer(
            viewers, many=True, context={"request": request}
        )
        return Response(serializer.data)


class DateInvitationViewSet(viewsets.ModelViewSet):
    """Приглашения на свидание."""

    serializer_class = DateInvitationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Оптимизация: select_related для from_user и to_user."""
        return DateInvitation.objects.select_related("from_user", "to_user").filter(
            Q(from_user=self.request.user) | Q(to_user=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        """Принять приглашение."""
        invitation = self.get_object()
        if invitation.to_user != request.user:
            return Response(
                {"detail": "Нет прав"},
                status=status.HTTP_403_FORBIDDEN,
            )
        invitation.status = DateInvitation.Status.ACCEPTED
        invitation.save()
        return Response(DateInvitationSerializer(invitation).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Отклонить приглашение."""
        invitation = self.get_object()
        if invitation.to_user != request.user:
            return Response(
                {"detail": "Нет прав"},
                status=status.HTTP_403_FORBIDDEN,
            )
        invitation.status = DateInvitation.Status.REJECTED
        invitation.save()
        return Response(DateInvitationSerializer(invitation).data)
