from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    uid = models.CharField(max_length=1500, primary_key=True)
    photoUrl = models.URLField(max_length=255, default='')

    USERNAME_FIELD = 'uid'
    REQUIRED_FIELDS = ['email', 'username', ]

    def __str__(self):
        return f'{self.email}'
