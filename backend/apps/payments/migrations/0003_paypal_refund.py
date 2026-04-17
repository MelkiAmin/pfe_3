from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    dependencies = [
        ('payments', '0002_wallet_transaction_withdrawalrequest'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='PayPalOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('paypal_order_id', models.CharField(blank=True, max_length=255)),
                ('paypal_capture_id', models.CharField(blank=True, max_length=255)),
                ('status', models.CharField(choices=[('created','Created'),('approved','Approved'),('completed','Completed'),('cancelled','Cancelled')], default='created', max_length=20)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paypal_orders', to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='events.event')),
            ],
            options={'db_table': 'paypal_orders', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('reason', models.TextField()),
                ('provider_refund_id', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='refund', to='payments.payment')),
            ],
            options={'db_table': 'refunds'},
        ),
    ]
