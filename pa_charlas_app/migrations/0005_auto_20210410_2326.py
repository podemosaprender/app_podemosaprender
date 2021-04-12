# Generated by Django 3.1.7 on 2021-04-10 23:26

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pa_charlas_app', '0004_voto_votoitem'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='visita',
            unique_together={('charla', 'de_quien')},
        ),
        migrations.AlterUniqueTogether(
            name='votoitem',
            unique_together={('de_quien', 'texto', 'voto')},
        ),
    ]