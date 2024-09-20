from django.contrib.auth.models import AbstractUser
from django.db import models

class UserMaster(AbstractUser):
    first_name = None
    last_name = None
    username = None
    last_login = None
    is_staff = None
    is_superuser = None
    date_joined = None
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    class Meta:
        db_table = "user_master"