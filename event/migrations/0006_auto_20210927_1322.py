# Generated by Django 3.2.7 on 2021-09-27 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0005_alter_event_photourl'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='photoUrl',
        ),
        migrations.AddField(
            model_name='event',
            name='fireId',
            field=models.CharField(default='', max_length=255),
        ),
    ]
