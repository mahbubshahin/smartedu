# Generated by Django 5.1 on 2025-05-23 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admission', '0013_homecontent_chairman_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homecontent',
            name='chairman_image',
            field=models.ImageField(blank=True, null=True, upload_to='chairman_img/'),
        ),
        migrations.AlterField(
            model_name='homecontent',
            name='co_ordinato_image',
            field=models.ImageField(blank=True, null=True, upload_to='coordinator_img/'),
        ),
    ]
