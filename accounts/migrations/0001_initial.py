# Generated by Django 5.1 on 2025-05-09 17:18

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('admission', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('role', models.CharField(choices=[('teacher', 'Teacher'), ('manager', 'Manager'), ('accountant', 'Accountant'), ('student', 'Student'), ('applicant', 'Applicant'), ('common_user', 'Common_User')], default='common_user', max_length=40)),
                ('full_name', models.CharField(max_length=70)),
                ('username', models.CharField(default='username', max_length=10, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('mobile_number', models.CharField(default='mobile', max_length=15, unique=True)),
                ('roll_number', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('is_email_verified', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('intake', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='admission.intake')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
