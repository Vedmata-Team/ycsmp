# Generated by Django 5.2.3 on 2025-07-11 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_eventregistration_email_sent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventregistration',
            name='country',
            field=models.CharField(blank=True, default='India', max_length=64, verbose_name='देश'),
        ),
    ]
