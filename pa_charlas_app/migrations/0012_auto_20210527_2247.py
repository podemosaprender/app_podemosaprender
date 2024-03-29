# Generated by Django 3.1.7 on 2021-05-27 22:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pa_charlas_app', '0011_bancotx'),
    ]

    operations = [
        migrations.AddField(
            model_name='bancotx',
            name='quien_hace',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='bancotx_hace', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='bancotx',
            name='quien_da',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bancotx_da', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='bancotx',
            name='quien_recibe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bancotx_recibe', to=settings.AUTH_USER_MODEL),
        ),
    ]
