from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.deletion import CASCADE

# Create your models here.


class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    venue = models.CharField(max_length=255)
    time = models.DateTimeField()
    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    fireId = models.CharField(max_length=255, default='')

    def __str__(self):
        return f'{self.name}'


class People(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    status = models.IntegerField(default=0)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.name}'


class Services(models.Model):
    name = models.CharField(max_length=100)
    organization = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    unitPrice = models.IntegerField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'


class Products(models.Model):
    name = models.CharField(max_length=100)
    organization = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    unitPrice = models.IntegerField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'
