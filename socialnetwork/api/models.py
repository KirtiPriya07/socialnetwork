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
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    class Meta:
        db_table = "user_master"

class FriendRequest(models.Model):
    sent_to =  models.ForeignKey(UserMaster, on_delete=models.CASCADE, related_name = "sent_to")
    sent_by =  models.ForeignKey(UserMaster, on_delete=models.CASCADE, related_name = "sent_by")
    status = models.CharField(max_length=10)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "friend_requests"
