# Generated by Django 5.1.6 on 2025-03-12 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_user_number_on_watchlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='number_on_watchlist',
            field=models.CharField(blank=True, max_length=8),
        ),
    ]
