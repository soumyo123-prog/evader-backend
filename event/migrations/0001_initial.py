# Generated by Django 3.2.7 on 2021-09-21 08:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=255)),
                ('venue', models.CharField(max_length=255)),
                ('time', models.DateTimeField()),
                ('photoUrl', models.URLField(max_length=300)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('people', models.ManyToManyField(related_name='People', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
