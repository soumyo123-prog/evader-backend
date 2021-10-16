from django.contrib import admin
from .models import Event, People, Expenditure

# Register your models here.
admin.site.register(Event)
admin.site.register(People)
admin.site.register(Expenditure)
