# Generated by Django 4.1 on 2022-09-04 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_unit_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='type',
            field=models.CharField(max_length=8),
        ),
    ]
