# Generated by Django 4.2.1 on 2023-08-09 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player_register', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='players',
            name='player_imgurl',
            field=models.TextField(default='https://t4.ftcdn.net/jpg/00/65/77/27/360_F_65772719_A1UV5kLi5nCEWI0BNLLiFaBPEkUbv5Fv.jpg'),
            preserve_default=False,
        ),
    ]
