"""
Intelligent Chatbot Service for Event Platform
Handles intent detection, database queries, and natural language responses
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from django.db.models import Q, Count
from django.utils import timezone
from .models import Event, Category

logger = logging.getLogger(__name__)


class Intent:
    GREETING = 'greeting'
    ASK_EVENTS = 'ask_events'
    FILTERED_SEARCH = 'filtered_search'
    HELP = 'help'
    UNKNOWN = 'unknown'


class ChatbotService:
    """Intelligent chatbot service for event discovery"""

    # French greeting patterns
    GREETING_PATTERNS = [
        r'\b(bonjour|salut|hello|hi|hey|bonsoir|coucou|ça va)\b',
        r'^/(bonjour|salut|hello)',
    ]

    # Category keywords mapping
    CATEGORY_KEYWORDS = {
        'concert': ['concert', 'musique', 'musical', 'chant', 'rock', 'jazz', 'pop', 'rap', 'dj'],
        'sport': ['sport', 'football', 'match', 'tennis', 'basket', 'course', 'marathon', 'fitness'],
        'business': ['business', 'entreprise', 'professionnel', 'conférence', 'meetup', 'startup', 'networking'],
        'culture': ['culture', 'théâtre', 'cinéma', 'exposition', 'musée', 'art', 'danse', 'spectacle'],
        'technologie': ['tech', 'technologie', 'coding', 'développement', 'digital', 'ia', 'ai', 'hackathon'],
        'food': ['food', 'gastronomie', 'restaurant', 'cuisine', 'foodie', 'dégustation'],
        'festival': ['festival', 'fête', 'célébration'],
    }

    # City keywords
    CITY_KEYWORDS = {
        'tunis': ['tunis', 'tunisie'],
        'sousse': ['sousse', 'sousse'],
        'sfax': ['sfax'],
        'monastir': ['monastir'],
        'mahdia': ['mahdia'],
        ' Hammamet': ['hammamet'],
        'kelibia': ['kélibia', 'kelibia'],
    }

    # Price keywords
    PRICE_KEYWORDS = {
        'free': ['gratuit', 'free', 'gratuite', 'pas cher', 'pas coûteux', ' gratuit'],
        'paid': ['payant', 'payante', 'cher', 'couteux', 'payé'],
    }

    # Date keywords
    DATE_KEYWORDS = {
        'today': ["aujourd'hui", "aujourd hui", "ce jour", "auj"],
        'tomorrow': ['demain', 'next day'],
        'this_week': ['cette semaine', 'cette sem', 'cette semaine'],
        'next_week': ['semaine prochaine', 'sem pro', 'la semaine prochaine'],
        'this_month': ['ce mois', 'ce mois ci', 'ce mois-ci'],
        'weekend': ['week-end', 'fin de semaine', 'w-e'],
    }

    def __init__(self):
        self.categories_cache = self._load_categories()

    def _load_categories(self) -> Dict[str, int]:
        """Load categories from database"""
        return {cat.name.lower(): cat.id for cat in Category.objects.all()}

    def detect_intent(self, message: str) -> Tuple[str, Dict[str, Any]]:
        """
        Detect user intent from message
        Returns: (intent, extracted_filters)
        """
        message_lower = message.lower().strip()

        # Check for greetings
        for pattern in self.GREETING_PATTERNS:
            if re.search(pattern, message_lower):
                return Intent.GREETING, {}

        # Check for help
        if any(word in message_lower for word in ['aide', 'help', 'comment ça marche', 'comment faire']):
            return Intent.HELP, {}

        # Check for events request
        event_keywords = [
            'événement', 'evenement', 'event', 'événements', 'evenements',
            'donner', 'afficher', 'liste', 'show', 'trouver', 'rechercher',
            'quels', 'quel', 'Quelles', 'quelle', 'y a t il', "y'a-t-il",
            'prochains', 'prochain', 'à venir', ' upcoming'
        ]
        has_event_keyword = any(kw in message_lower for kw in event_keywords)

        # Check for filters
        filters = self._extract_filters(message_lower)

        if has_event_keyword or filters:
            return Intent.FILTERED_SEARCH, filters

        if any(word in message_lower for word in event_keywords):
            return Intent.ASK_EVENTS, {}

        return Intent.UNKNOWN, {}

    def _extract_filters(self, message: str) -> Dict[str, Any]:
        """Extract search filters from message"""
        filters = {}

        # Extract category
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in message for kw in keywords):
                filters['category'] = category
                break

        # Extract city
        for city, keywords in self.CITY_KEYWORDS.items():
            if any(kw in message for kw in keywords):
                filters['city'] = city
                break

        # Extract price
        for price_type, keywords in self.PRICE_KEYWORDS.items():
            if any(kw in message for kw in keywords):
                filters['is_free'] = price_type == 'free'
                break

        # Extract date
        for date_type, keywords in self.DATE_KEYWORDS.items():
            if any(kw in message for kw in keywords):
                filters['date'] = date_type
                break

        return filters

    def query_events(self, filters: Dict[str, Any], limit: int = 5) -> List[Event]:
        """Query events based on filters"""
        queryset = Event.objects.filter(
            status=Event.Status.APPROVED,
            start_date__gte=timezone.now()
        ).select_related('category', 'organizer').order_by('start_date')

        # Apply category filter
        if 'category' in filters:
            category_name = filters['category']
            # Search in category name or tags
            queryset = queryset.filter(
                Q(category__name__icontains=category_name) |
                Q(tags__contains=[category_name])
            )

        # Apply city filter
        if 'city' in filters:
            city = filters['city']
            queryset = queryset.filter(
                Q(city__icontains=city) |
                Q(address__icontains=city)
            )

        # Apply price filter
        if 'is_free' in filters:
            queryset = queryset.filter(is_free=filters['is_free'])

        # Apply date filter
        if 'date' in filters:
            date_filter = filters['date']
            today = timezone.now().date()

            if date_filter == 'today':
                queryset = queryset.filter(start_date__date=today)
            elif date_filter == 'tomorrow':
                tomorrow = today + timedelta(days=1)
                queryset = queryset.filter(start_date__date=tomorrow)
            elif date_filter == 'this_week':
                week_end = today + timedelta(days=7)
                queryset = queryset.filter(start_date__date__range=[today, week_end])
            elif date_filter == 'next_week':
                week_start = today + timedelta(days=7)
                week_end = today + timedelta(days=14)
                queryset = queryset.filter(start_date__date__range=[week_start, week_end])
            elif date_filter == 'this_month':
                from datetime import datetime
                month_end = today.replace(day=28) + timedelta(days=4)
                month_end = month_end.replace(day=1) - timedelta(days=1)
                queryset = queryset.filter(start_date__date__range=[today, month_end])
            elif date_filter == 'weekend':
                # Get next Friday to Sunday
                days_until_friday = (4 - today.weekday()) % 7
                if days_until_friday == 0:
                    days_until_friday = 7
                friday = today + timedelta(days=days_until_friday)
                sunday = friday + timedelta(days=2)
                queryset = queryset.filter(start_date__date__range=[friday, sunday])

        # If no filters, return popular/upcoming events
        if not filters:
            queryset = queryset.annotate(
                ticket_count=Count('tickets')
            ).order_by('-ticket_count', 'start_date')

        return list(queryset[:limit])

    def get_popular_events(self, limit: int = 5) -> List[Event]:
        """Get popular events based on ticket sales"""
        return list(Event.objects.filter(
            status=Event.Status.APPROVED,
            start_date__gte=timezone.now()
        ).annotate(
            ticket_count=Count('tickets')
        ).order_by('-ticket_count', 'start_date')[:limit])

    def get_recent_events(self, limit: int = 5) -> List[Event]:
        """Get recently added events"""
        return list(Event.objects.filter(
            status=Event.Status.APPROVED,
            start_date__gte=timezone.now()
        ).order_by('-created_at')[:limit])

    def format_events_response(self, events: List[Event], context: str = "") -> str:
        """Format events into natural language response"""
        if not events:
            return "Je n'ai trouvé aucun événement correspondant à vos critères 😔\n\n" \
                   "Essayez de modifier votre recherche ou consultez tous nos événements."

        response_parts = []

        if context:
            response_parts.append(f"Voici les événements que j'ai trouvés {context}:")
        else:
            response_parts.append("Voici quelques événements disponibles:")

        for i, event in enumerate(events, 1):
            date_str = event.start_date.strftime('%d/%m/%Y à %Hh%M')
            price_str = "Gratuit" if event.is_free else "Payant"
            location = event.city if event.city else event.venue_name if event.venue_name else "En ligne"

            event_line = f"\n{i}. **{event.title}**"
            event_line += f"\n   📅 {date_str}"
            event_line += f"\n   📍 {location}"
            event_line += f"\n   💰 {price_str}"

            if event.category:
                event_line += f"\n   🏷️ {event.category.name}"

            response_parts.append(event_line)

        response_parts.append("\n\nCliquez sur un événement pour plus de détails!")

        return '\n'.join(response_parts)

    def get_greeting_response(self) -> str:
        """Get greeting response"""
        greetings = [
            "Bonjour! 👋 Je suis votre assistant événementiel.",
            "Salut! 🎉 Je suis là pour vous aider à trouver des événements.",
            "Hello! 🙋 Je peux vous aider à découvrir des événements passionnants.",
        ]
        import random
        greeting = random.choice(greetings)

        return greeting + "\n\nVous pouvez me demander:\n" \
               "• \"Quels événements à Tunis?\"\n" \
               "• \"Des concerts ce week-end\"\n" \
               "• \"Événements gratuits\"\n" \
               "• \"Des activités sport\"\n\nTapez ce que vous recherchez!"

    def get_help_response(self) -> str:
        """Get help response"""
        return "Je peux vous aider à trouver des événements! 🎯\n\n" \
               "**Exemples de questions:**\n" \
               "• \"Donner moi les événements\"\n" \
               "• \"Concerts à Tunis\"\n" \
               "• \"Événements sportifs ce week-end\"\n" \
               "• \"Festivals gratuits\"\n" \
               "• \"Conférences ce mois\"\n\n" \
               "Je peux filtrer par:\n" \
               "📍 Ville (Tunis, Sousse, etc.)\n" \
               "🏷️ Catégorie (concert, sport, culture, tech)\n" \
               "💰 Prix (gratuit, pas cher)\n" \
               "📅 Date (aujourd'hui, ce week-end, ce mois)\n\n" \
               "Que recherchez-vous?"

    def get_unknown_response(self) -> str:
        """Get response for unknown intent"""
        return "Je n'ai pas bien compris votre demande 😕\n\n" \
               "Essayez de me dire:\n" \
               "• \"Quels événements disponibles\"\n" \
               "• \"Concerts à Tunis\"\n" \
               "• \"Événements ce week-end\"\n\n" \
               "Ou tapez \"aide\" pour voir mes possibilités!"

    def process_message(self, message: str) -> Dict[str, Any]:
        """
        Main method to process user message
        Returns dict with 'response' and 'events'
        """
        try:
            intent, filters = self.detect_intent(message)
            logger.info(f"[Chatbot] Intent: {intent}, Filters: {filters}")

            if intent == Intent.GREETING:
                response_text = self.get_greeting_response()
                events = self.get_popular_events(3)

            elif intent == Intent.HELP:
                response_text = self.get_help_response()
                events = self.get_popular_events(3)

            elif intent == Intent.ASK_EVENTS:
                events = self.query_events(filters) if filters else self.get_popular_events(5)
                context = self._build_context(filters)
                response_text = self.format_events_response(events, context)

            elif intent == Intent.FILTERED_SEARCH:
                events = self.query_events(filters)

                if not events:
                    # Try fallback to popular events
                    fallback_events = self.get_popular_events(3)
                    response_text = "Je n'ai pas trouvé d'événements exactement matching votre recherche.\n\n" \
                                    "Voici quelques événements populaires:\n"
                    response_text += self.format_events_response(fallback_events, "").split('\n\n')[0]
                    events = fallback_events
                else:
                    context = self._build_context(filters)
                    response_text = self.format_events_response(events, context)

            else:
                response_text = self.get_unknown_response()
                events = self.get_popular_events(3)

            return {
                'response': response_text,
                'events': events,
                'intent': intent,
                'filters': filters
            }

        except Exception as e:
            logger.error(f"[Chatbot] Error: {str(e)}")
            return {
                'response': "Désolé, une erreur s'est produite. Veuillez réessayer.",
                'events': [],
                'intent': 'error',
                'filters': {}
            }

    def _build_context(self, filters: Dict[str, Any]) -> str:
        """Build context string for response"""
        parts = []

        if 'city' in filters:
            parts.append(f"à {filters['city'].capitalize()}")

        if 'category' in filters:
            category = filters['category']
            if category == 'concert':
                parts.append(f"de {category}s")
            else:
                parts.append(f"en {category}")

        if 'date' in filters:
            date_map = {
                'today': "aujourd'hui",
                'tomorrow': 'demain',
                'this_week': 'cette semaine',
                'next_week': 'la semaine prochaine',
                'this_month': 'ce mois',
                'weekend': 'ce week-end'
            }
            date_str = date_map.get(filters['date'], filters['date'])
            parts.append(date_str)

        if 'is_free' in filters:
            parts.append("gratuits" if filters['is_free'] else "payants")

        return " ".join(parts) if parts else ""


# Singleton instance
chatbot_service = ChatbotService()
