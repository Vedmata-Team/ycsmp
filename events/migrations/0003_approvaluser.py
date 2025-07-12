# Generated manually for ApprovalUser model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0002_eventregistration_approval_status_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApprovalUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state_code', models.CharField(max_length=10, verbose_name='राज्य कोड')),
                ('is_state_approver', models.BooleanField(default=False, verbose_name='राज्य अप्रूवर')),
                ('is_district_approver', models.BooleanField(default=False, verbose_name='जिला अप्रूवर')),
                ('districts', models.JSONField(blank=True, default=list, verbose_name='जिले')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='यूजर')),
            ],
            options={
                'verbose_name': 'अप्रूवल यूजर',
                'verbose_name_plural': 'अप्रूवल यूजर',
            },
        ),
    ]