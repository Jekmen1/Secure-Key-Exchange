from rest_framework.routers import DefaultRouter
from .views import ChannelViewSet, SecretExchangeView, KeyGenerationView
from django.urls import path, include

router = DefaultRouter()
router.register(r'channels', ChannelViewSet, basename='channel')

urlpatterns = [
    path('', include(router.urls)),
    path('channels/<int:channel_id>/secret/', SecretExchangeView.as_view(), name='secret-exchange'),
    path('channels/<int:channel_id>/generate_key/', KeyGenerationView.as_view(), name='key-generation'),
]