from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import User

class UserManagerTest(TestCase):

	def test_create_user(self):
		User = get_user_model()
		user = User.objects.create_user(username='user', password='password')
		self.assertEqual(user.username, 'user')
		self.assertTrue(user.is_active)
		self.assertFalse(user.is_admin)
		self.assertTrue(user.check_password('password'))
		with self.assertRaises(TypeError):
			User.objects.create_user()
		with self.assertRaises(TypeError):
			User.objects.create_user(username='')

	def test_create_superuser(self):
		User = get_user_model()
		user = User.objects.create_superuser(username='user', password='password')
		self.assertEqual(user.username, 'user')
		self.assertTrue(user.is_active)
		self.assertTrue(user.is_admin)
		self.assertTrue(user.check_password('password'))
		with self.assertRaises(TypeError):
			User.objects.create_superuser()
		with self.assertRaises(TypeError):
			User.objects.create_superuser(username='')
