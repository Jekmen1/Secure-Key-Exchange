from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from .models import Channel


class ChannelApiTestCase(APITestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='testsender', password='password123')
        self.recipient = User.objects.create_user(username='testrecipient', password='password123')
        self.client = APIClient()

    def test_create_channel(self):
        self.client.login(username='testsender', password='password123')
        response = self.client.post(reverse('channel-list'), {'recipient_user': self.recipient.id})
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.client.logout()

    def test_retrieve_channel(self):
        channel = Channel.objects.create(sender_user=self.sender, recipient_user=self.recipient, name='channel1')
        self.client.login(username='testsender', password='password123')
        response = self.client.get(reverse('channel-detail', kwargs={'pk': channel.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

    def test_accept_channel(self):
        channel = Channel.objects.create(sender_user=self.sender, recipient_user=self.recipient, name='channel1')
        self.client.login(username='testrecipient', password='password123')
        response = self.client.post(reverse('channel-accept', kwargs={'pk': channel.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()

    def test_secret_exchange_recipient(self):
        channel = Channel.objects.create(sender_user=self.sender, recipient_user=self.recipient, name='channel1',
                                         accepted=True)
        self.client.login(username='testrecipient', password='password123')
        response = self.client.post(reverse('secret-exchange', kwargs={'channel_id': channel.id}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('recipient_secret', response.data)
        self.client.logout()

    def test_secret_exchange_sender(self):
        channel = Channel.objects.create(sender_user=self.sender, recipient_user=self.recipient,
                                         name='channel1',
                                         accepted=True)
        self.client.login(username='testsender', password='password123')
        response = self.client.post(reverse('secret-exchange', kwargs={'channel_id': channel.id}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('sender_secret', response.data)
        self.client.logout()

    def test_key_generation_sender(self):
        channel = Channel.objects.create(
            sender_user=self.sender,
            recipient_user=self.recipient,
            name='channel1',
            accepted=True,
            initial_sender_secret='123456789',
            initial_recipient_secret='987654321'
        )
        self.client.login(username='testsender', password='password123')
        response = self.client.get(reverse('key-generation', kwargs={'channel_id': channel.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('shared_key', response.data)
        self.client.logout()

    def test_key_generation_recipient(self):
        channel = Channel.objects.create(
            sender_user=self.sender,
            recipient_user=self.recipient,
            name='channel1',
            accepted=True,
            initial_sender_secret='123456789',
            initial_recipient_secret='987654321'
        )
        self.client.login(username='testrecipient', password='password123')
        response = self.client.get(reverse('key-generation', kwargs={'channel_id': channel.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('shared_key', response.data)
        self.client.logout()

