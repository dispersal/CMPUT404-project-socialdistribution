# Generated by Django 2.1.7 on 2019-04-06 01:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0017_server_trailing_slash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='description',
            field=models.CharField(default='', max_length=400),
        ),
    ]
