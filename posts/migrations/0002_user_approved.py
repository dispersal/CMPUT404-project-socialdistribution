# Generated by Django 2.1.5 on 2019-03-03 21:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='approved',
            field=models.BooleanField(default=False),
        ),
    ]