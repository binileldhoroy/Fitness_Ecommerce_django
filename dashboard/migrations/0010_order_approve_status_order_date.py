# Generated by Django 4.0.2 on 2022-02-16 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_alter_payment_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='approve_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='date',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
