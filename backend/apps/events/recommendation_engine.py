"""
Système de recommandation d'événements basé sur:
- Historique des réservations utilisateur
- Catégories préférées
- Popularité des événements
"""

from django.db.models import Count, Q
from django.utils import timezone
from typing import List, Optional
import logging

from .models import Event, Category
from apps.tickets.models import Ticket

logger = logging.getLogger(__name__)


def get_user_preferred_categories(user) -> List[Category]:
    """
    Extrait les catégories préférées de l'utilisateur basées sur son historique de réservations.
    """
    if not user.is_authenticated:
        return []
    
    reserved_events = Event.objects.filter(
        tickets__attendee=user,
        tickets__status__in=[Ticket.Status.CONFIRMED, Ticket.Status.USED]
    ).values_list('category_id', flat=True).distinct()
    
    category_ids = [cat_id for cat_id in reserved_events if cat_id is not None]
    
    if not category_ids:
        return list(Category.objects.all()[:5])
    
    from collections import Counter
    category_counts = Counter(category_ids)
    preferred_ids = [cat_id for cat_id, _ in category_counts.most_common(3)]
    
    return list(Category.objects.filter(id__in=preferred_ids))


def get_user_reserved_event_ids(user) -> List[int]:
    """
    Retourne les IDs des événements déjà réservés par l'utilisateur.
    """
    if not user.is_authenticated:
        return []
    
    return list(
        Ticket.objects.filter(
            attendee=user,
            status__in=[Ticket.Status.CONFIRMED, Ticket.Status.USED]
        ).values_list('event_id', flat=True).distinct()
    )


def get_popular_events(limit: int = 10) -> List[Event]:
    """
    Retourne les événements les plus populaires (par nombre de réservations).
    """
    return list(
        Event.objects.filter(
            status=Event.Status.APPROVED,
            start_date__gte=timezone.now()
        )
        .annotate(reservation_count=Count('tickets', filter=Q(tickets__status=Ticket.Status.CONFIRMED)))
        .order_by('-reservation_count', '-start_date')[:limit]
    )


def recommend_events(
    user,
    limit: int = 10,
    use_ml: bool = False
) -> List[Event]:
    """
    Fonction principale de recommandation d'événements.
    
    Args:
        user: Utilisateur pour lequel générer des recommandations
        limit: Nombre d'événements à retourner
        use_ml: Si True, utilise le filtrage collaboratif (optionnel)
    
    Returns:
        Liste d'événements recommandés
    """
    if not user.is_authenticated:
        return get_popular_events(limit)
    
    reserved_event_ids = get_user_reserved_event_ids(user)
    preferred_categories = get_user_preferred_categories(user)
    
    base_query = Event.objects.filter(
        status=Event.Status.APPROVED,
        start_date__gte=timezone.now()
    ).select_related('organizer', 'category')
    
    if reserved_event_ids:
        base_query = base_query.exclude(id__in=reserved_event_ids)
    
    if preferred_categories:
        category_ids = [cat.id for cat in preferred_categories]
        base_query = base_query.annotate(
            reservation_count=Count('tickets', filter=Q(tickets__status=Ticket.Status.CONFIRMED))
        )
        
        from django.db.models import Case, When, IntegerField
        from django.db.models.functions import Coalesce
        
        prioritized_events = sorted(
            list(base_query.all()),
            key=lambda e: (
                e.category_id in category_ids,
                e.reservation_count if hasattr(e, 'reservation_count') else 0,
                e.average_rating
            ),
            reverse=True
        )
        
        recommended = prioritized_events[:limit]
    else:
        recommended = list(
            base_query.annotate(
                reservation_count=Count('tickets', filter=Q(tickets__status=Ticket.Status.CONFIRMED))
            )
            .order_by('-reservation_count', '-average_rating', '-start_date')[:limit]
        )
    
    if len(recommended) < limit:
        additional_needed = limit - len(recommended)
        additional = list(
            Event.objects.filter(
                status=Event.Status.APPROVED,
                start_date__gte=timezone.now()
            )
            .exclude(id__in=[e.id for e in recommended])
            .exclude(id__in=reserved_event_ids)
            .order_by('-start_date')[:additional_needed]
        )
        recommended.extend(additional)
    
    return recommended[:limit]


def get_similar_events(event: Event, limit: int = 5) -> List[Event]:
    """
    Retourne des événements similaires basés sur la catégorie et les tags.
    """
    similar = Event.objects.filter(
        status=Event.Status.APPROVED,
        start_date__gte=timezone.now()
    ).exclude(id=event.id)
    
    if event.category:
        similar = similar.filter(category=event.category)
    
    similar = similar.annotate(
        reservation_count=Count('tickets', filter=Q(tickets__status=Ticket.Status.CONFIRMED))
    )
    
    return list(similar.order_by('-reservation_count', '-start_date')[:limit])
