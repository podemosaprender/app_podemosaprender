# Generated by Django 3.1.7 on 2022-06-24 02:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pa_charlas_app', '0014_bancotx'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvisoModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fh_creado', models.DateTimeField(auto_now_add=True, help_text='Fecha y hora en qeu el modelo fue creado', verbose_name='creado a las ')),
                ('fh_modificado', models.DateTimeField(auto_now=True, help_text='Fecha y hora en qeu el modelo fue editado', verbose_name='modificado a las ')),
                ('titulo', models.CharField(max_length=200)),
                ('detalle', models.TextField()),
                ('precio', models.FloatField(help_text='Precio del aviso reflejado en PodemosTokens')),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Aviso',
                'verbose_name_plural': 'Avisos',
            },
        ),
    ]
