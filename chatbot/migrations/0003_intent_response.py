# Generated by Django 4.2.16 on 2024-09-12 05:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0002_chatanalytics_webhook_chatmessage_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Intent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('keywords', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('intent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='chatbot.intent')),
            ],
        ),
    ]