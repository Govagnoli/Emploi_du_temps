# Generated by Django 4.1.7 on 2023-04-14 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_alter_tache_end_alter_tache_start'),
    ]

    operations = [
        migrations.CreateModel(
            name='Abscence',
            fields=[
                ('id_abs', models.AutoField(primary_key=True, serialize=False)),
                ('motif', models.CharField(blank=True, max_length=50, null=True)),
                ('start', models.DateField(blank=True, null=True)),
                ('end', models.DateField(blank=True, null=True)),
            ],
        ),
    ]
