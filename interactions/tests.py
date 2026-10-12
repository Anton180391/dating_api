from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import DateInvitation, Interaction, ProfileView

User = get_user_model()


class BaseTestCase(APITestCase):
    """Базовая настройка — два пользователя."""

    def setUp(self):
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="test12345",
            first_name="Антон",
            last_name="Тестов",
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="test12345",
            first_name="Мария",
            last_name="Иванова",
        )


# ═══════════════════════════════════════════════════════════
# ЛАЙК / ДИЗЛАЙК
# ═══════════════════════════════════════════════════════════


class InteractionTests(BaseTestCase):
    """Тесты лайков и дизлайков."""

    def test_create_like(self):
        """Лайк создаётся через POST."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            "/api/interactions/",
            {"to_user": self.user2.id, "type": "like"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Interaction.objects.count(), 1)

    def test_create_dislike(self):
        """Дизлайк создаётся через POST."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            "/api/interactions/",
            {"to_user": self.user2.id, "type": "dislike"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_likes_count_increments(self):
        """Счётчик лайков увеличивается."""
        self.client.force_authenticate(user=self.user1)
        self.assertEqual(self.user2.likes_count, 0)

        self.client.post(
            "/api/interactions/",
            {"to_user": self.user2.id, "type": "like"},
            format="json",
        )
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.likes_count, 1)

    def test_dislike_does_not_increment_likes(self):
        """Дизлайк НЕ увеличивает счётчик лайков."""
        self.client.force_authenticate(user=self.user1)
        self.client.post(
            "/api/interactions/",
            {"to_user": self.user2.id, "type": "dislike"},
            format="json",
        )
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.likes_count, 0)

    def test_cannot_like_self(self):
        """Нельзя лайкнуть самого себя."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            "/api/interactions/",
            {"to_user": self.user1.id, "type": "like"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_like_twice(self):
        """Нельзя лайкнуть дважды одного и того же."""
        self.client.force_authenticate(user=self.user1)
        self.client.post(
            "/api/interactions/",
            {"to_user": self.user2.id, "type": "like"},
            format="json",
        )
        response = self.client.post(
            "/api/interactions/",
            {"to_user": self.user2.id, "type": "like"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_cannot_like(self):
        """Неавторизованный не может лайкнуть."""
        response = self.client.post(
            "/api/interactions/",
            {"to_user": self.user2.id, "type": "like"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_my_likes(self):
        """Список моих лайков."""
        Interaction.objects.create(
            from_user=self.user1, to_user=self.user2, type=Interaction.Type.LIKE
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.get("/api/interactions/my-likes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_my_dislikes(self):
        """Список моих дизлайков."""
        Interaction.objects.create(
            from_user=self.user1, to_user=self.user2, type=Interaction.Type.DISLIKE
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.get("/api/interactions/my-dislikes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_liked_me(self):
        """Кто лайкнул меня."""
        Interaction.objects.create(
            from_user=self.user1, to_user=self.user2, type=Interaction.Type.LIKE
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.get("/api/interactions/liked-me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_mutual_likes(self):
        """Взаимные лайки."""
        Interaction.objects.create(
            from_user=self.user1, to_user=self.user2, type=Interaction.Type.LIKE
        )
        Interaction.objects.create(
            from_user=self.user2, to_user=self.user1, type=Interaction.Type.LIKE
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.get("/api/interactions/mutual/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_mutual_empty_without_both_likes(self):
        """Взаимных лайков нет, если лайкнул только один."""
        Interaction.objects.create(
            from_user=self.user1, to_user=self.user2, type=Interaction.Type.LIKE
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.get("/api/interactions/mutual/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


# ═══════════════════════════════════════════════════════════
# ПРИГЛАШЕНИЯ
# ═══════════════════════════════════════════════════════════


class DateInvitationTests(BaseTestCase):
    """Тесты приглашений."""

    def setUp(self):
        super().setUp()
        # Взаимные лайки — чтобы приглашение прошло валидацию
        Interaction.objects.create(
            from_user=self.user1, to_user=self.user2, type=Interaction.Type.LIKE
        )
        Interaction.objects.create(
            from_user=self.user2, to_user=self.user1, type=Interaction.Type.LIKE
        )

    def test_create_invitation_mutual(self):
        """Приглашение создаётся при взаимных лайках."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            "/api/invitations/",
            {"to_user": self.user2.id, "message": "Пойдём в кафе"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invitation_without_mutual_fails(self):
        """Без взаимных лайков приглашение не создаётся."""
        user3 = User.objects.create_user(
            email="user3@example.com",
            password="test12345",
            first_name="Пётр",
            last_name="Петров",
        )
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            "/api/invitations/",
            {"to_user": user3.id, "message": "Привет"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_invitation(self):
        """Получатель может принять приглашение."""
        invitation = DateInvitation.objects.create(
            from_user=self.user1, to_user=self.user2, message="Привет"
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f"/api/invitations/{invitation.id}/accept/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, DateInvitation.Status.ACCEPTED)

    def test_reject_invitation(self):
        """Получатель может отклонить приглашение."""
        invitation = DateInvitation.objects.create(
            from_user=self.user1, to_user=self.user2, message="Привет"
        )
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f"/api/invitations/{invitation.id}/reject/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, DateInvitation.Status.REJECTED)

    def test_only_recipient_can_accept(self):
        """Только получатель может принять."""
        invitation = DateInvitation.objects.create(
            from_user=self.user1, to_user=self.user2, message="Привет"
        )
        self.client.force_authenticate(user=self.user1)  # ← отправитель
        response = self.client.post(f"/api/invitations/{invitation.id}/accept/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# ═══════════════════════════════════════════════════════════
# ПРОСМОТРЫ
# ═══════════════════════════════════════════════════════════


class ProfileViewTests(BaseTestCase):
    """Тесты истории просмотров."""

    def test_create_view(self):
        """Просмотр создаётся."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            "/api/views/",
            {"viewed": self.user2.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProfileView.objects.count(), 1)

    def test_who_viewed_me(self):
        """Кто смотрел меня."""
        ProfileView.objects.create(viewer=self.user1, viewed=self.user2)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get("/api/views/who-viewed-me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
