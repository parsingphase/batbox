# Generated by Django 2.2.2 on 2019-06-07 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracemap', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='audiorecording',
            name='duration',
            field=models.FloatField(blank=True, null=True),
        ),
    ]