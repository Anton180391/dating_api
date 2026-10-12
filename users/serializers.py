from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Hobby, UserPhoto

User = get_user_model()


class HobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hobby
        fields = ["id", "name"]


class UserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPhoto
        fields = ["id", "image", "order", "created_at"]
        read_only_fields = ["created_at"]


class UserListSerializer(serializers.ModelSerializer):
    """Краткая информация — для списка."""

    full_name = serializers.CharField(read_only=True)
    main_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "gender",
            "age",
            "city",
            "status",
            "main_photo_url",
            "likes_count",
        ]

    def get_main_photo_url(self, obj):
        if obj.main_photo and obj.main_photo.image:
            request = self.context.get("request")
            url = obj.main_photo.image.url
            return request.build_absolute_uri(url) if request else url
        return None


class UserDetailSerializer(serializers.ModelSerializer):
    """Полная информация — для детальной страницы."""

    full_name = serializers.CharField(read_only=True)
    hobbies = HobbySerializer(many=True, read_only=True)
    photos = UserPhotoSerializer(many=True, read_only=True)
    main_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "full_name",
            "first_name",
            "last_name",
            "patronymic",
            "gender",
            "age",
            "city",
            "hobbies",
            "status",
            "photos",
            "main_photo_url",
            "likes_count",
            "show_age",
            "show_city",
            "show_hobbies",
            "show_online",
            "created_at",
        ]

    def get_main_photo_url(self, obj):
        if obj.main_photo and obj.main_photo.image:
            request = self.context.get("request")
            url = obj.main_photo.image.url
            return request.build_absolute_uri(url) if request else url
        return None


class UserRegisterSerializer(serializers.ModelSerializer):
    """Регистрация через email."""

    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "patronymic",
            "gender",
            "age",
            "city",
        ]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Пароли не совпадают.")
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Обновление профиля."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "patronymic",
            "gender",
            "age",
            "city",
            "hobbies",
            "status",
            "main_photo",
            "show_age",
            "show_city",
            "show_hobbies",
            "show_online",
        ]
