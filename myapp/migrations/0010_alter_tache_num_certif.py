# Generated by Django 4.1.7 on 2023-04-24 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_alter_tache_id_tache'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tache',
            name='num_certif',
            field=models.BigIntegerField(null=True),
        ),
    ]