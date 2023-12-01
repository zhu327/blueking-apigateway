# Generated by Django 3.2.18 on 2023-11-27 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metrics', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='StatisticsAPIRequestByDay',
            new_name='StatisticsGatewayRequestByDay',
        ),
        migrations.RenameField(
            model_name='statisticsgatewayrequestbyday',
            old_name='api_id',
            new_name='gateway_id',
        ),
        migrations.AlterField(
            model_name='statisticsgatewayrequestbyday',
            name='gateway_id',
            field=models.IntegerField(db_column='api_id', db_index=True),
        ),
        migrations.RenameField(
            model_name='statisticsapprequestbyday',
            old_name='api_id',
            new_name='gateway_id',
        ),
        migrations.AlterField(
            model_name='statisticsapprequestbyday',
            name='gateway_id',
            field=models.IntegerField(db_column='api_id', db_index=True),
        ),
    ]
