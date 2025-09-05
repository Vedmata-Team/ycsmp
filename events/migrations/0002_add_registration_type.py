from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventregistration',
            name='registration_type',
            field=models.CharField(
                choices=[('participant', 'प्रतिभागी'), ('volunteer', 'समयदानी कार्यकर्ता')],
                default='participant',
                max_length=20,
                verbose_name='पंजीकरण प्रकार'
            ),
        ),
    ]