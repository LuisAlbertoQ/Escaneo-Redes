# Generated by Django 5.1.3 on 2024-11-24 01:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Escaneo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_hora', models.DateTimeField(auto_now_add=True)),
                ('rango_ips', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Dispositivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField()),
                ('mac', models.CharField(blank=True, max_length=50, null=True)),
                ('nombre', models.CharField(blank=True, max_length=100, null=True)),
                ('estado', models.CharField(choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')], max_length=10)),
                ('sistema_operativo', models.CharField(blank=True, max_length=100, null=True)),
                ('fabricante', models.CharField(blank=True, max_length=100, null=True)),
                ('tipo', models.CharField(choices=[('PC', 'PC'), ('Móvil', 'Móvil'), ('Otro', 'Otro')], default='Otro', max_length=20)),
                ('escaneo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dispositivos', to='monitor.escaneo')),
            ],
        ),
    ]
