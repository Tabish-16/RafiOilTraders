# Generated by Django 5.0.7 on 2024-07-31 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=100, null=True)),
                ('vehicle_Type', models.CharField(blank=True, max_length=300, null=True)),
                ('registeration_num', models.CharField(blank=True, max_length=300, null=True)),
                ('date', models.DateField()),
                ('last_reading', models.CharField(blank=True, max_length=500, null=True)),
                ('next_reading', models.CharField(blank=True, max_length=500, null=True)),
                ('next_changing_date', models.DateField()),
            ],
        ),
    ]