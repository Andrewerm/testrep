# Generated by Django 3.1.7 on 2021-06-07 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crmApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aliproducts',
            name='freight_template_id',
            field=models.IntegerField(verbose_name='freight template id'),
        ),
    ]
