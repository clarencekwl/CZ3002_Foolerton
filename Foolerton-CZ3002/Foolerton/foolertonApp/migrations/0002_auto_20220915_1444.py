# Generated by Django 3.2.13 on 2022-09-15 06:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foolertonApp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comments',
            old_name='date',
            new_name='editDate',
        ),
        migrations.AddField(
            model_name='comments',
            name='editBy',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='editBy',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='editDate',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='task',
            name='number',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comments',
            name='comment',
            field=models.CharField(blank=True, max_length=160, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='task',
            name='details',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]
