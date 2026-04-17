from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ATTENDEE = 'attendee', 'Attendee'
        ORGANIZER = 'organizer', 'Organizer'
        ADMIN = 'admin', 'Admin'

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ATTENDEE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_2fa_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=64, blank=True)
    two_factor_enabled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.first_name} {self.last_name} <{self.email}>'

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    @property
    def is_organizer(self) -> bool:
        return self.role == self.Role.ORGANIZER

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN

    def enable_two_factor(self, secret: str):
        self.two_factor_secret = secret
        self.is_2fa_enabled = True
        self.two_factor_enabled_at = timezone.now()
        self.save(update_fields=['two_factor_secret', 'is_2fa_enabled', 'two_factor_enabled_at', 'updated_at'])

    def disable_two_factor(self):
        self.two_factor_secret = ''
        self.is_2fa_enabled = False
        self.two_factor_enabled_at = None
        self.save(update_fields=['two_factor_secret', 'is_2fa_enabled', 'two_factor_enabled_at', 'updated_at'])
