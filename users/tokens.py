from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT-сериализатор для входа по email."""

    username_field = "email"


class EmailTokenObtainPairView(TokenObtainPairView):
    """JWT-view для входа по email."""

    serializer_class = EmailTokenObtainPairSerializer
