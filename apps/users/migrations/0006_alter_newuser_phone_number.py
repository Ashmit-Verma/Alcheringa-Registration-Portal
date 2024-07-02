# Generated by Django 4.2.4 on 2023-12-11 07:38

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_newuser_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newuser',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=14, region=None),
        ),
    ]
