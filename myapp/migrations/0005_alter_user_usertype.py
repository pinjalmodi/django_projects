# Generated by Django 5.1.1 on 2024-10-01 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='usertype',
            field=models.CharField(choices=[('admin', 'admin'), ('member', 'member')], default='member', max_length=100),
        ),
    ]
