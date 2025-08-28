from django.db import models
from django.contrib.auth.models import User


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    class Gender(models.TextChoices):
        MALE = "M"
        FEMALE = "F"
    gender = models.CharField(choices=Gender.choices, max_length=1)
