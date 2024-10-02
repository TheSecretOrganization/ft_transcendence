from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
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

class AddFriendTest(TestCase):
	def setUp(self):
		username = 'bob'
		password = 'pBrp#fg4LKDeg8$X'
		self.route = '/friends/invite/'
		self.user = get_user_model().objects.create_user(username=username, password=password)
		self.target = get_user_model().objects.create_user(username='mich', password=password)
		self.client.login(username=username, password=password)

	def test_add_friend(self):
		request = post(self.client, self.route, {'target': self.target.id})
		self.assertEqual(request.status_code, 200, 'Invite failed')
		invite = Friend.objects.get(origin=self.user.id, target=self.target.id)
		self.assertIsNotNone(invite, 'Invite has not been found in database')
		self.assertEqual(invite.status, Friend.Status.PENDING, 'Default status is not PENDING')
		self.assertEqual(invite.origin, self.user, 'Origin is not the user')
		self.assertEqual(invite.target, self.target, 'Target is not the right target')

	def test_add_friend_already_send(self):
		with transaction.atomic():
			request = post(self.client, self.route, {'target': self.target.id})
			self.assertEqual(request.status_code, 200, 'Badic invite failed')
		with transaction.atomic():
			request = post(self.client, self.route, {'target': self.target.id})
			self.assertEqual(request.status_code, 400, 'Server accepted duplicated invite')
		count = Friend.objects.filter(origin=self.user, target=self.target).count()
		self.assertEqual(count, 1, 'There is more than 1 entry for friend invite')

	def test_add_friend_without_param(self):
		request = post(self.client, self.route, None)
		self.assertEqual(request.status_code, 400, "None argument didn't result in a 400")
		request = post(self.client, self.route, {})
		self.assertEqual(request.status_code, 400, "Empty argument didn't result in a 400")
		request = post(self.client, self.route, {'traget': self.target.id})
		self.assertEqual(request.status_code, 400, "Wront argument didn't result in a 400")

	def test_add_friend_not_logged(self):
		self.client.logout()
		request = post(self.client, self.route, {'target': self.target.id})
		self.assertEqual(request.status_code, 401, "Not logged user didn't result in a 401")
		self.assertFalse(Friend.objects.filter(origin=self.user, target=self.target).exists(),
				   "Not logged user created an entry in database")
	
	def test_add_friend_self(self):
		with transaction.atomic():
			request = post(self.client, self.route, {'target': self.user.id})
			self.assertEqual(request.status_code, 400, "Self invite didn't result in a 400")
		self.assertFalse(Friend.objects.filter(origin=self.user, target=self.user).exists(),
				   "Self invite created an entry in database")

	def test_add_unknown_friend(self):
		rid = 404
		request = post(self.client, self.route, {'target': rid})
		self.assertEqual(request.status_code, 400, "Unknown target didn't result in a 400")
		self.assertFalse(Friend.objects.filter(origin=self.user, target=404).exists(),
				   "Self invite created an entry in database")

class AcceptFriendTest(TestCase):
	def setUp(self):
		self.route = '/friends/accept/'
		self.user = get_user_model().objects.create_user(username='testuser', password='password')
		self.user2 = get_user_model().objects.create_user(username='testuser2', password='password')
		self.client.login(username='testuser', password='password')
		self.invite = Friend.objects.create(origin=self.user2, target=self.user)

	def test_accept_invite_success(self):
		response = post(self.client, self.route, {'invite_id': self.invite.id})
		self.assertEqual(response.status_code, 200)
		self.invite.refresh_from_db()
		self.assertEqual(self.invite.status, Friend.Status.ACCEPTED)

	def test_accept_invite_not_authenticated(self):
		self.client.logout()
		response = post(self.client, self.route, {'invite_id': self.invite.id})
		self.assertEqual(response.status_code, 401)
		self.invite.refresh_from_db()
		self.assertEqual(self.invite.status, Friend.Status.PENDING)

	def test_accept_invite_missing_arguments(self):
		response = post(self.client, self.route, {})
		self.assertEqual(response.status_code, 400)
		response = post(self.client, self.route, {'id_invite': 1})
		self.assertEqual(response.status_code, 400)

	def test_accept_invite_does_not_exist(self):
		response = post(self.client, self.route, {'invite_id': 999})
		self.assertEqual(response.status_code, 400)
	
	def test_accept_already_denied_invite(self):
		self.invite.status = Friend.Status.DENIED
		self.invite.save()
		response = post(self.client, self.route, {'invite_id': self.invite.id})
		self.assertEqual(response.status_code, 400)
		self.invite.refresh_from_db()
		self.assertEqual(self.invite.status, Friend.Status.DENIED)

class DenyFriendTest(TestCase):
	def setUp(self):
		self.route = '/friends/deny/'
		self.user = get_user_model().objects.create_user(username='testuser', password='password')
		self.user2 = get_user_model().objects.create_user(username='testuser2', password='password')
		self.client.login(username='testuser', password='password')
		self.invite = Friend.objects.create(origin=self.user2, target=self.user)

	def test_deny_invite_success(self):
		response = post(self.client, self.route, {'invite_id': self.invite.id})
		self.assertEqual(response.status_code, 200)
		self.invite.refresh_from_db()
		self.assertEqual(self.invite.status, Friend.Status.DENIED)

	def test_deny_invite_not_authenticated(self):
		self.client.logout()
		response = post(self.client, self.route, {'invite_id': self.invite.id})
		self.assertEqual(response.status_code, 401)
		self.invite.refresh_from_db()
		self.assertEqual(self.invite.status, Friend.Status.PENDING)

	def test_deny_invite_missing_arguments(self):
		response = post(self.client, self.route, {})
		self.assertEqual(response.status_code, 400)
		response = post(self.client, self.route, {'id_invite': 1})
		self.assertEqual(response.status_code, 400)

	def test_deny_invite_does_not_exist(self):
		response = post(self.client, self.route, {'invite_id': 999})
		self.assertEqual(response.status_code, 400)

	def test_deny_already_accepted_invite(self):
		self.invite.status = Friend.Status.ACCEPTED
		self.invite.save()
		response = post(self.client, self.route, {'invite_id': self.invite.id})
		self.assertEqual(response.status_code, 400)
		self.invite.refresh_from_db()
		self.assertEqual(self.invite.status, Friend.Status.ACCEPTED)
