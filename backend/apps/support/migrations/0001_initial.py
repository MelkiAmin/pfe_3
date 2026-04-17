from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name='SupportTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('ticket_ref', models.CharField(editable=False, max_length=12, unique=True)),
                ('subject', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('open','Open'),('in_review','In Review'),('resolved','Resolved'),('closed','Closed')], default='open', max_length=20)),
                ('priority', models.CharField(choices=[('low','Low'),('medium','Medium'),('high','High'),('urgent','Urgent')], default='medium', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='support_tickets', to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'support_tickets', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='SupportMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('is_staff', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='support.supportticket')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'support_messages', 'ordering': ['created_at']},
        ),
    ]
