from django.contrib import admin
from .models import Event, People, Services, Products

# Register your models here.
admin.site.register(Event)
admin.site.register(People)
admin.site.register(Services)
admin.site.register(Products)
