# Generated by Django 4.1.7 on 2023-04-14 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_abscence'),
    ]

    operations = [
        migrations.AddField(
            model_name='techniciens',
            name='abscence',
            field=models.ManyToManyField(to='myapp.abscence'),
        ),
    ]
