# Generated by Django 3.2.16 on 2023-06-13 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0016_auto_20230613_1436'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'verbose_name': 'комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
        migrations.AddField(
            model_name='comment',
            name='is_published',
            field=models.BooleanField(default=True, help_text='Снимите галочку, чтобы скрыть публикацию.', verbose_name='Опубликовано'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Добавлено'),
        ),
    ]
