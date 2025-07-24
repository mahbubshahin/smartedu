from django.db import models

# Create your models here.


from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from datetime import datetime


from django.core.validators import MinValueValidator, MaxValueValidator


from django.db.models.signals import post_save, post_delete
from django.core.exceptions import ValidationError
from django.dispatch import receiver


# for gpa chek

from django.core.validators import RegexValidator


from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class AccountManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)  
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, username, password, **extra_fields)

class UserRegistration(AbstractBaseUser, PermissionsMixin):  # ✅ PermissionsMixin যোগ করা হয়েছে যাতে করে এডমিন প্যানেল থেকে গ্রুপ পারমিশন দিতে পারি।

    TEACHER = 'teacher'
    MANAGER = 'manager'
    STUDENT = 'student'
    ACCOUNTANT = 'accountant'
    APPLICANT = 'applicant'
    

    ROLE_CHOICES = [
        
        (TEACHER, 'Teacher'),
        (MANAGER, 'Manager'),
        (STUDENT, 'Student'),
        (ACCOUNTANT, 'Accountant'),
        (APPLICANT, 'Applicant'),        
        
    ]

    role = models.CharField(max_length=40, choices=ROLE_CHOICES,)
    full_name = models.CharField(max_length=70, blank=False, null=False)
    username = models.CharField(max_length=10, blank=False, null=False, unique=True,)
    email = models.EmailField(unique=True, blank=False, null=False)
    mobile_number = models.CharField(max_length=15, unique=True, blank=False, null=False, default='mobile')
    intake = models.ForeignKey('admission.Intake', on_delete=models.SET_NULL, null=True, blank=True)

    roll_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    position_no = models.IntegerField(blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True) 

    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Custom manager
    objects = AccountManager()

    def __str__(self):
        return self.full_name

    # Custom permission system (optional — PermissionsMixin handle kore)
    def has_function(self, function_code):
        return self.user_functions.filter(function=function_code, active=True).exists()

    def get_all_functions(self):
        return [uf.function for uf in self.user_functions.all()]

