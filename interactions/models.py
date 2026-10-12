from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Interaction(models.Model):
    """
    Взаимодействие между пользователями: лайк или дизлайк.
    """

    class Type(models.TextChoices):
        LIKE = "like", "Лайк"
        DISLIKE = "dislike", "Дизлайк"

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="interactions_sent",
        verbose_name="От кого",
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="interactions_received",
        verbose_name="Кому",
    )
    type = models.CharField(
        "Тип",
        max_length=10,
        choices=Type.choices,
    )
    created_at = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        verbose_name = "Взаимодействие"
        verbose_name_plural = "Взаимодействия"
        ordering = ["-created_at"]
        unique_together = ("from_user", "to_user")  # один пользователь — одна реакция

    def __str__(self):
        return f"{self.from_user} → {self.to_user} ({self.type})"

    def clean(self):
        """Валидация: нельзя лайкать самого себя."""
        super().clean()
        if self.from_user == self.to_user:
            raise ValidationError("Нельзя лайкать самого себя.")


class ProfileView(models.Model):
    """
    История просмотров профилей.
    """

    viewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="views_made",
        verbose_name="Кто смотрел",
    )
    viewed = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="views_received",
        verbose_name="Кого смотрели",
    )
    viewed_at = models.DateTimeField("Дата просмотра", auto_now_add=True)

    class Meta:
        verbose_name = "Просмотр профиля"
        verbose_name_plural = "История просмотров"
        ordering = ["-viewed_at"]

    def __str__(self):
        return f"{self.viewer} смотрел {self.viewed}"


class DateInvitation(models.Model):
    """
    Приглашение на свидание / обмен контактами.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает"
        ACCEPTED = "accepted", "Принято"
        REJECTED = "rejected", "Отклонено"

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invitations_sent",
        verbose_name="От кого",
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invitations_received",
        verbose_name="Кому",
    )
    message = models.TextField("Сообщение", blank=True)
    contact_info = models.CharField(
        "Контакт",
        max_length=200,
        blank=True,
        help_text="Телефон, email или соцсеть для связи",
    )
    status = models.CharField(
        "Статус",
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField("Отправлено", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Приглашение на свидание"
        verbose_name_plural = "Приглашения на свидание"
        ordering = ["-created_at"]
        unique_together = ("from_user", "to_user")

    def __str__(self):
        return f"{self.from_user} → {self.to_user} ({self.status})"

    def clean(self):
        """Валидация: только между взаимолайкнувшими."""
        super().clean()

        if self.from_user == self.to_user:
            raise ValidationError("Нельзя пригласить самого себя.")

        # Проверяем взаимные лайки
        if self.from_user_id and self.to_user_id:
            mutual = (
                Interaction.objects.filter(
                    from_user=self.from_user,
                    to_user=self.to_user,
                    type=Interaction.Type.LIKE,
                ).exists()
                and Interaction.objects.filter(
                    from_user=self.to_user,
                    to_user=self.from_user,
                    type=Interaction.Type.LIKE,
                ).exists()
            )
            if not mutual:
                raise ValidationError(
                    "Приглашение возможно только при взаимных лайках."
                )
