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
        extra_fields.setdefault('status', User.Status.APPROVED)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ATTENDEE = 'attendee', 'Attendee'
        ORGANIZER = 'organizer', 'Organizer'
        ADMIN = 'admin', 'Admin'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ATTENDEE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPROVED)
    status_note = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    banned_at = models.DateTimeField(null=True, blank=True)
    ban_reason = models.TextField(blank=True)
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

    @property
    def is_banned(self) -> bool:
        return not self.is_active

    def ban(self, reason: str = ''):
        self.is_active = False
        self.banned_at = timezone.now()
        self.ban_reason = reason
        self.save(update_fields=['is_active', 'banned_at', 'ban_reason', 'updated_at'])

    def unban(self):
        self.is_active = True
        self.banned_at = None
        self.ban_reason = ''
        self.save(update_fields=['is_active', 'banned_at', 'ban_reason', 'updated_at'])

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
