# Generated by Django 4.2.3 on 2023-07-30 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cakes', '0004_alter_deliverytime_delivery_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='cake',
            name='standard',
            field=models.BooleanField(default=True, verbose_name='Стандартный'),
        ),
        migrations.AlterField(
            model_name='cake',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Вес'),
        ),
    ]
