from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_seed_default_accounts'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='ban_reason',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='banned_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
