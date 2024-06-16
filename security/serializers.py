from rest_framework import serializers
from .models import Channel

class ChannelSerializer(serializers.ModelSerializer):
    sender_user = serializers.ReadOnlyField(source='sender_user.username')
    recipient_user = serializers.ReadOnlyField(source='recipient_user.username')
    name = serializers.ReadOnlyField()

    class Meta:
        model = Channel
        fields = ['id', 'name', 'sender_user', 'recipient_user']
