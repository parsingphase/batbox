# Generated by Django 2.2.2 on 2019-06-23 15:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracemap', '0006_species_mdd_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='audiorecording',
            old_name='is_noise',
            new_name='hide',
        ),
    ]
