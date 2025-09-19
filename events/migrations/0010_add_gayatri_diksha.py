# Generated migration for gayatri_diksha field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_alter_eventregistration_aadhar_back_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventregistration',
            name='gayatri_diksha',
            field=models.BooleanField(blank=True, null=True, verbose_name='क्या आपने गायत्री दीक्षा ली है?'),
        ),
    ]