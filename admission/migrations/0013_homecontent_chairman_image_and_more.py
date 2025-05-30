# Generated by Django 5.1 on 2025-05-23 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admission', '0012_remove_maingallery_chairman_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='homecontent',
            name='chairman_image',
            field=models.ImageField(blank=True, null=True, upload_to='department_img/'),
        ),
        migrations.AddField(
            model_name='homecontent',
            name='co_ordinato_image',
            field=models.ImageField(blank=True, null=True, upload_to='department_img/'),
        ),
        migrations.AlterField(
            model_name='maingallery',
            name='heading',
            field=models.CharField(blank=True, max_length=35, null=True),
        ),
    ]
