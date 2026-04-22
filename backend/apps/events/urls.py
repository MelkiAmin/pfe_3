from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet, basename='category')
router.register('favorites', views.FavoriteViewSet, basename='favorite')
router.register('reviews', views.EventReviewViewSet, basename='event-review')
router.register('chatbot', views.ChatbotViewSet, basename='chatbot')
router.register('', views.EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
]
