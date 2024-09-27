from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from .models import Friend
import json

def post(client, url, content):
	return client.post(url, json.dumps(content), content_type='application/json')

class FriendTest(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username='bob', password='123')
		self.target = get_user_model().objects.create_user(username='mich', password='123')

	def test_create_base(self):
		friend = Friend.objects.create(origin=self.user, target=self.target)
		self.assertIsNotNone(friend)
		self.assertEqual(friend.origin, self.user)
		self.assertEqual(friend.target, self.target)
		self.assertEqual(friend.status, Friend.Status.PENDING)

	def test_double_invite(self):
		invite = Friend.objects.create(origin=self.user, target=self.target)
		self.assertIsNotNone(invite)
		with self.assertRaises(IntegrityError):
			Friend.objects.create(origin=self.user, target=self.target)

	def test_cross_invite(self):
		invite = Friend.objects.create(origin=self.user, target=self.target)
		self.assertIsNotNone(invite)
		with self.assertRaises(ValidationError):
			Friend.objects.create(origin=self.target, target=self.user)

	def test_invite_self(self):
		with self.assertRaises(IntegrityError):
			Friend.objects.create(origin=self.user, target=self.user)
