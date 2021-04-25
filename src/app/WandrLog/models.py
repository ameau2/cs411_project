# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class Destination(models.Model):
    city_name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    country_code = models.CharField(max_length=3)
    destination_picture = models.BinaryField(blank=True, null=True)
    website_link = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'destination'


class Favorites(models.Model):
    traveller_id = models.IntegerField()
    dest_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'favorites'


class Friend(models.Model):
    traveller_id = models.IntegerField()
    friend_id = models.IntegerField()
    date_of_friendship = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'friend'

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Traveler(AbstractBaseUser):
    objects = UserManager()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    password = models.CharField(max_length=1025)
    address = models.CharField(max_length=1025, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=255, unique=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.BinaryField(blank=True, null=True)
    credit_card_info = models.CharField(max_length=255, blank=True, null=True)
    date_joined = models.DateField(blank=True, null=True)
    last_login = models.DateField(blank=True, null=True)
    is_admin = models.BooleanField(blank=True, null=True, default=False)
    is_active = models.BooleanField(blank=True, null=True,default=True)
    is_staff = models.BooleanField(blank=True, null=True, default=False)
    is_superuser = models.BooleanField(blank=True, null=True, default=False)




    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Email & Password are required by default

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    class Meta:
        managed = False
        db_table = 'traveler'



