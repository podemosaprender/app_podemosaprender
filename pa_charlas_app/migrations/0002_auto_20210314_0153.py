# Generated by Django 3.1.7 on 2021-03-13 03:21

from django.db import migrations

def crear_tipo_charla(apps, schema_editor):
    TipoCharla= apps.get_model('pa_charlas_app','TipoCharla')	
    TipoCharla(titulo='Tema').save()

class Migration(migrations.Migration):

    dependencies = [
        ('pa_charlas_app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_tipo_charla)
    ]
