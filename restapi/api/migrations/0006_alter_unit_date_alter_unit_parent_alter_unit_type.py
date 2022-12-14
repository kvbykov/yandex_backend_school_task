# Generated by Django 4.1 on 2022-09-04 10:44

import api.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_history_parentid_alter_history_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='date',
            field=models.DateTimeField(validators=[api.validators.validate_date]),
        ),
        migrations.AlterField(
            model_name='unit',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.unit', validators=[api.validators.validate_parent]),
        ),
        migrations.AlterField(
            model_name='unit',
            name='type',
            field=models.CharField(max_length=8, validators=[api.validators.validate_type]),
        ),
    ]
