# Generated by Django 4.2.4 on 2023-12-19 08:42

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_newuser_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teammembers',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Others')], default='M', max_length=1),
        ),
        migrations.AlterField(
            model_name='teammembers',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None),
        ),
    ]
