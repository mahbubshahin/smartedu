# Generated by Django 5.1 on 2025-05-09 17:18

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Intake',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Program_name', models.CharField(max_length=200)),
                ('intake_name', models.CharField(max_length=255)),
                ('degree_name', models.CharField(blank=True, max_length=255, null=True)),
                ('batch_name', models.CharField(max_length=255)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('admit_download', models.DateTimeField()),
                ('admission_test', models.DateTimeField()),
                ('result_publish', models.DateField()),
                ('merit_list_admission', models.CharField(blank=True, max_length=100, null=True)),
                ('waiting_list_admission', models.CharField(blank=True, max_length=100, null=True)),
                ('orientation', models.DateField()),
                ('is_open', models.BooleanField(default=False)),
                ('create_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
