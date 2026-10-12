from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class UserManager(BaseUserManager):
    """Менеджер для кастомного User (email вместо username)."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Создаёт пользователя с email и паролем."""
        if not email:
            raise ValueError("Email обязателен.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Обычный пользователь."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Суперпользователь."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомная модель пользователя.

    Авторизация через email (вместо username).
    """

    class Gender(models.TextChoices):
        MALE = "M", "Мужской"
        FEMALE = "F", "Женский"
        OTHER = "O", "Другой"

    class Status(models.TextChoices):
        SEARCHING = "searching", "В поиске"
        BUSY = "busy", "Занят"
        MARRIED = "married", "Женат/Замужем"
        NOT_SEARCHING = "not_searching", "Не ищу"

    # ═══════════════════════════════════════════════════════════
    # АВТОРИЗАЦИЯ ЧЕРЕЗ EMAIL
    # ═══════════════════════════════════════════════════════════
    email = models.EmailField("Email", unique=True)
    username = models.CharField(
        "Username",
        max_length=150,
        unique=True,
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"  # ← логинимся по email
    REQUIRED_FIELDS = ["username"]  # ← что ещё спрашивать

    # ═══════════════════════════════════════════════════════════
    # ПРОФИЛЬ
    # ═══════════════════════════════════════════════════════════
    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100)
    patronymic = models.CharField("Отчество", max_length=100, blank=True)
    gender = models.CharField(
        "Пол",
        max_length=1,
        choices=Gender.choices,
        default=Gender.OTHER,
    )
    age = models.PositiveSmallIntegerField(
        "Возраст",
        null=True,
        blank=True,
        validators=[MinValueValidator(18), MaxValueValidator(120)],
    )
    city = models.CharField("Город", max_length=100, blank=True)
    hobbies = models.ManyToManyField(
        "Hobby",
        blank=True,
        related_name="users",
        verbose_name="Увлечения",
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.SEARCHING,
    )
    main_photo = models.ForeignKey(
        "UserPhoto",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="main_for_users",
        verbose_name="Заглавное фото",
    )

    # ═══════════════════════════════════════════════════════════
    # НАСТРОЙКИ ПРИВАТНОСТИ
    # ═══════════════════════════════════════════════════════════
    show_age = models.BooleanField("Показывать возраст", default=True)
    show_city = models.BooleanField("Показывать город", default=True)
    show_hobbies = models.BooleanField("Показывать увлечения", default=True)
    show_online = models.BooleanField("Показывать онлайн", default=True)

    # ═══════════════════════════════════════════════════════════
    # СЛУЖЕБНЫЕ ПОЛЯ
    # ═══════════════════════════════════════════════════════════
    likes_count = models.PositiveIntegerField("Количество лайков", default=0)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    # ═══════════════════════════════════════════════════════════
    # МЕНЕДЖЕР (для create_user / create_superuser)
    # ═══════════════════════════════════════════════════════════
    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email or self.username or f"User #{self.pk}"

    @property
    def full_name(self):
        """Полное имя."""
        parts = [self.last_name, self.first_name, self.patronymic]
        return " ".join(p for p in parts if p) or self.email


class Hobby(models.Model):
    """Увлечение (спорт, музыка, книги и т.д.)."""

    name = models.CharField("Название", max_length=100, unique=True)

    class Meta:
        verbose_name = "Увлечение"
        verbose_name_plural = "Увлечения"
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserPhoto(models.Model):
    """Фотография в галерее пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="Пользователь",
    )
    image = models.ImageField("Фото", upload_to="users/photos/%Y/%m/%d/")
    order = models.PositiveIntegerField("Порядок", default=0)
    created_at = models.DateTimeField("Загружено", auto_now_add=True)

    class Meta:
        verbose_name = "Фото пользователя"
        verbose_name_plural = "Фото пользователей"
        ordering = ["order", "id"]

    def __str__(self):
        return f"Фото #{self.order} — {self.user}"

    def delete(self, *args, **kwargs):
        """Удаляем файл с диска при удалении записи."""
        self.image.delete(save=False)
        super().delete(*args, **kwargs)
