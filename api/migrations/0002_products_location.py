# Generated by Django 2.0.7 on 2018-08-02 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='location',
            field=models.CharField(default='no location', max_length=40),
            preserve_default=False,
        ),
    ]