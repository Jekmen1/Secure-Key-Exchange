import os
from .models import Channel, User
from .serializers import ChannelSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings


class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer

    def perform_create(self, serializer):
        name = os.urandom(5).hex()
        recipient_user_id = self.request.data.get('recipient_user')
        recipient_user = get_object_or_404(User, pk=recipient_user_id)
        serializer.save(sender_user=self.request.user, recipient_user=recipient_user, name=name)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        channel = get_object_or_404(Channel, pk=pk)
        if channel.recipient_user != request.user:
            return Response({'error': 'You are not the recipient of this channel'}, status=status.HTTP_403_FORBIDDEN)
        channel.accepted = True
        channel.save()
        return Response({'status': 'channel accepted'})


class SecretExchangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, channel_id):
        channel = get_object_or_404(Channel, id=channel_id)

        if not channel.accepted:
            return Response({'error': 'Channel has not been accepted'}, status=status.HTTP_400_BAD_REQUEST)

        secret_key = int.from_bytes(os.urandom(32), byteorder='big')
        initial_secret = pow(settings.BASE, secret_key, settings.MODULUS)
        if request.user == channel.sender_user:
            channel.initial_sender_secret = initial_secret
            channel.save()
            return Response({'sender_secret': initial_secret}, status=status.HTTP_201_CREATED)
        elif request.user == channel.recipient_user:
            channel.initial_recipient_secret = initial_secret
            channel.save()
            return Response({'recipient_secret': initial_secret}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'You are not authorized for this channel'}, status=status.HTTP_403_FORBIDDEN)


class KeyGenerationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, channel_id):
        channel = get_object_or_404(Channel, id=channel_id)

        if not channel.accepted:
            return Response({'error': 'Channel has not been accepted'}, status=status.HTTP_400_BAD_REQUEST)
        if not channel.initial_sender_secret or not channel.initial_recipient_secret:
            return Response({'error': 'Initial secrets are not set'}, status=status.HTTP_400_BAD_REQUEST)

        secret_key = int.from_bytes(os.urandom(32))

        if request.user == channel.sender_user:
            shared_key = pow(int(channel.initial_recipient_secret), secret_key, settings.MODULUS)
            return Response({'shared_key': shared_key}, status=status.HTTP_200_OK)
        elif request.user == channel.recipient_user:
            shared_key = pow(int(channel.initial_sender_secret), secret_key, settings.MODULUS)
            return Response({'shared_key': shared_key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'You are not authorized for this channel'}, status=status.HTTP_403_FORBIDDEN)






