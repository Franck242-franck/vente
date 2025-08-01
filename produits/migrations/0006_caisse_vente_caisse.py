# Generated by Django 5.2.1 on 2025-07-28 03:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produits', '0005_historiquevente'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Caisse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_ouverture', models.DateField(auto_now_add=True)),
                ('date_fermeture', models.DateField(blank=True, null=True)),
                ('total_journalier', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('statut', models.CharField(choices=[('ouverte', 'Ouverte'), ('fermée', 'Fermée')], default='ouverte', max_length=10)),
                ('utilisateur', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='vente',
            name='caisse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='produits.caisse'),
        ),
    ]
