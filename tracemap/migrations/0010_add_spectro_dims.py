# Generated by Django 2.2.7 on 2020-07-25 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracemap', '0009_add_iso_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='audiorecording',
            name='spectrogram_image_height',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='audiorecording',
            name='spectrogram_image_width',
            field=models.IntegerField(null=True),
        ),
    ]
