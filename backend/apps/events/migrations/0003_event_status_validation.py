from django.db import migrations, models


def migrate_event_statuses(apps, schema_editor):
    Event = apps.get_model('events', 'Event')
    status_map = {
        'draft': 'pending',
        'published': 'approved',
        'cancelled': 'rejected',
    }
    for old_status, new_status in status_map.items():
        Event.objects.filter(status=old_status).update(status=new_status)


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_favorite_eventreview'),
    ]

    operations = [
        migrations.RunPython(migrate_event_statuses, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                    ('cancelled', 'Cancelled'),
                    ('completed', 'Completed'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
    ]
