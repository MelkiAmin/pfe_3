import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'planova.settings')
django.setup()

from apps.accounts.models import User
from apps.events.models import Event, Category
from apps.tickets.models import TicketType
from django.utils import timezone
from datetime import timedelta
import uuid

# Create categories
categories_data = [
    {'name': 'Concert', 'slug': 'concert', 'description': 'Concerts et spectacles musicaux'},
    {'name': 'Sport', 'slug': 'sport', 'description': 'Evenements sportifs'},
    {'name': 'Culture', 'slug': 'culture', 'description': 'Arts et culture'},
    {'name': 'Technologie', 'slug': 'technologie', 'description': 'Evenements tech et innovation'},
    {'name': 'Business', 'slug': 'business', 'description': 'Evenements professionnels'},
]

for cat_data in categories_data:
    Category.objects.get_or_create(slug=cat_data['slug'], defaults=cat_data)

print('Categories created:', Category.objects.count())

# Get organizer
org = User.objects.filter(role='organizer').first()
if not org:
    org = User.objects.filter(role='admin').first()

if org:
    # Create approved events for chatbot testing
    events_data = [
        {'title': 'Jazz Night au Theatre', 'category': 'concert', 'city': 'Tunis', 'is_free': False, 'price': 50},
        {'title': 'Match de Football ES Tunis', 'category': 'sport', 'city': 'Tunis', 'is_free': True, 'price': 0},
        {'title': 'Exposition Art Moderne', 'category': 'culture', 'city': 'Sousse', 'is_free': True, 'price': 0},
        {'title': 'Tech Conference 2024', 'category': 'technologie', 'city': 'Tunis', 'is_free': False, 'price': 100},
        {'title': 'Networking Business Day', 'category': 'business', 'city': 'Tunis', 'is_free': False, 'price': 75},
    ]
    
    for i, ev_data in enumerate(events_data):
        cat = Category.objects.get(slug=ev_data['category'])
        slug = ev_data['title'].lower().replace(' ', '-') + '-' + uuid.uuid4().hex[:6]
        
        event, created = Event.objects.get_or_create(
            slug=slug,
            defaults={
                'organizer': org,
                'category': cat,
                'title': ev_data['title'],
                'description': 'Un evenement ' + ev_data['category'] + ' incroyable a ' + ev_data['city'],
                'city': ev_data['city'],
                'status': 'approved',
                'is_free': ev_data['is_free'],
                'start_date': timezone.now() + timedelta(days=i+1),
                'end_date': timezone.now() + timedelta(days=i+1, hours=3),
            }
        )
        
        if created:
            price = ev_data['price'] if ev_data['price'] > 0 else 0
            TicketType.objects.get_or_create(
                event=event,
                name='Standard',
                defaults={'price': price, 'quantity': 100}
            )
            print('Created:', event.title)
    
    print('Total approved events:', Event.objects.filter(status='approved').count())
else:
    print('No organizer found')