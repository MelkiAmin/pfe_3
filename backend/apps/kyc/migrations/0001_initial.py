from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name='KYCDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('doc_type', models.CharField(choices=[('passport','Passport'),('national_id','National ID'),('driver_license','Driver License')], max_length=30)),
                ('front_image', models.ImageField(blank=True, null=True, upload_to='kyc/docs/')),
                ('back_image',  models.ImageField(blank=True, null=True, upload_to='kyc/docs/')),
                ('selfie',      models.ImageField(blank=True, null=True, upload_to='kyc/selfies/')),
                ('status', models.CharField(choices=[('pending','Pending'),('approved','Approved'),('rejected','Rejected')], default='pending', max_length=20)),
                ('rejection_reason', models.TextField(blank=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at',  models.DateTimeField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='kyc', to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'kyc_documents'},
        ),
    ]
