# Generated manually for email_sent field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_approvaluser'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventregistration',
            name='email_sent',
            field=models.BooleanField(default=False, verbose_name='ईमेल भेजा गया'),
        ),
    ]