# Generated by Django 5.1 on 2024-09-27 10:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Pending'), (2, 'Accepted'), (3, 'Denied')], default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('origin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origin', to=settings.AUTH_USER_MODEL)),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('origin', 'target'), name='unique_friend_request'), models.CheckConstraint(condition=models.Q(('origin', models.F('target')), _negated=True), name='unique_origin_target')],
            },
        ),
    ]
