# Generated by Django 5.1 on 2025-05-12 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admission', '0006_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='intake',
            name='coordinator_signature',
            field=models.ImageField(blank=True, null=True, upload_to='coordinator_signatures/'),
        ),
    ]
