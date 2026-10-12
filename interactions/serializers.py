from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import DateInvitation, Interaction, ProfileView

User = get_user_model()


class InteractionSerializer(serializers.ModelSerializer):
    from_user_email = serializers.CharField(source="from_user.email", read_only=True)
    to_user_email = serializers.CharField(source="to_user.email", read_only=True)

    class Meta:
        model = Interaction
        fields = [
            "id",
            "from_user",
            "from_user_email",
            "to_user",
            "to_user_email",
            "type",
            "created_at",
        ]
        read_only_fields = ["from_user", "created_at"]

    def validate(self, data):
        """Валидация: нельзя лайкать самого себя, нельзя дважды."""
        request = self.context.get("request")
        from_user = request.user if request else None
        to_user = data.get("to_user")

        if from_user and to_user and from_user == to_user:
            raise serializers.ValidationError("Нельзя лайкать самого себя.")

        # Проверяем, нет ли уже такого взаимодействия
        if from_user and to_user:
            if Interaction.objects.filter(
                from_user=from_user, to_user=to_user
            ).exists():
                raise serializers.ValidationError(
                    "Вы уже взаимодействовали с этим пользователем."
                )

        return data


class ProfileViewSerializer(serializers.ModelSerializer):
    viewer_email = serializers.CharField(source="viewer.email", read_only=True)
    viewed_email = serializers.CharField(source="viewed.email", read_only=True)

    class Meta:
        model = ProfileView
        fields = [
            "id",
            "viewer",
            "viewer_email",
            "viewed",
            "viewed_email",
            "viewed_at",
        ]
        read_only_fields = ["viewer", "viewed_at"]


class DateInvitationSerializer(serializers.ModelSerializer):
    from_user_email = serializers.CharField(source="from_user.email", read_only=True)
    to_user_email = serializers.CharField(source="to_user.email", read_only=True)

    class Meta:
        model = DateInvitation
        fields = [
            "id",
            "from_user",
            "from_user_email",
            "to_user",
            "to_user_email",
            "message",
            "contact_info",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["from_user", "status", "created_at", "updated_at"]

    def validate(self, data):
        """Валидация: только между взаимолайкнувшими."""
        request = self.context.get("request")
        from_user = request.user if request else None
        to_user = data.get("to_user")

        if from_user and to_user and from_user == to_user:
            raise serializers.ValidationError("Нельзя пригласить самого себя.")

        if from_user and to_user:
            mutual = (
                Interaction.objects.filter(
                    from_user=from_user,
                    to_user=to_user,
                    type=Interaction.Type.LIKE,
                ).exists()
                and Interaction.objects.filter(
                    from_user=to_user,
                    to_user=from_user,
                    type=Interaction.Type.LIKE,
                ).exists()
            )
            if not mutual:
                raise serializers.ValidationError(
                    "Приглашение возможно только при взаимных лайках."
                )

        return data
