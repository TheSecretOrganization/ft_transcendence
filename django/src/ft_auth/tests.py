from django.contrib.auth import get_user_model
from django.test import Client, TestCase

class UserManagerTest(TestCase):

	def test_create_user(self):
		user_model = get_user_model()
		user = user_model.objects.create_user(username='user', password='password')
		self.assertEqual(user.username, 'user')
		self.assertTrue(user.is_active)
		self.assertFalse(user.is_admin)
		self.assertTrue(user.check_password('password'))
		with self.assertRaises(TypeError):
			user_model.objects.create_user()
		with self.assertRaises(TypeError):
			user_model.objects.create_user(username='')

	def test_create_superuser(self):
		user_model = get_user_model()
		user = user_model.objects.create_superuser(username='user', password='password')
		self.assertEqual(user.username, 'user')
		self.assertTrue(user.is_active)
		self.assertTrue(user.is_admin)
		self.assertTrue(user.check_password('password'))
		with self.assertRaises(TypeError):
			user_model.objects.create_superuser()
		with self.assertRaises(TypeError):
			user_model.objects.create_superuser(username='')

class LoginTest(TestCase):

	def setUp(self):
		self.client = Client()
		get_user_model().objects.create_user(username='mich', password='mich334@')

	def test_login_without_param(self):
		request = self.client.post('/auth/login/')
		self.assertEqual(request.status_code, 400)
		self.assertFalse('user_id' in self.client.session)
		request = self.client.post('/auth/login/', {'username': 'mich'})
		self.assertEqual(request.status_code, 400)
		self.assertFalse('user_id' in self.client.session)
		request = self.client.post('/auth/login/', {'password': 'mich443@'})
		self.assertEqual(request.status_code, 400)
		self.assertFalse('user_id' in self.client.session)

	def test_login_wrong_credentials(self):
		request = self.client.post('/auth/login/', {'username': 'mich', 'password': 'mich334'})
		self.assertEqual(request.status_code, 401)
		self.assertFalse('user_id' in self.client.session)

	def test_login(self):
		request = self.client.post('/auth/login/', {'username': 'mich', 'password': 'mich334@'})
		self.assertEqual(request.status_code, 200)
		self.assertTrue('user_id' in self.client.session)
	
	def test_logout_without_login(self):
		request = self.client.get('/auth/logout/')
		self.assertEqual(request.status_code, 401)

	def test_logout(self):
		request = self.client.post('/auth/login/', {'username': 'mich', 'password': 'mich334@'})
		self.assertEqual(request.status_code, 200)
		self.assertTrue('user_id' in self.client.session)
		request = self.client.get('/auth/logout/')
		self.assertEqual(request.status_code, 200)
		self.assertFalse('user_id' in self.client.session)

class RegisterTest(TestCase):

	def setUp(self):
		self.client = Client()

	def test_register_without_param(self):
		request = self.client.post('/auth/register/')
		self.assertEqual(request.status_code, 400)
		request = self.client.post('/auth/register/', {'username': 'ok'})
		self.assertEqual(request.status_code, 400)
		request = self.client.post('/auth/register/', {'password': 'ok'})
		self.assertEqual(request.status_code, 400)

	def test_register(self):
		request = self.client.post('/auth/register/', {
			'username': 'mich',
			'password': 'mich334@',
		})
		self.assertEqual(request.status_code, 200)
		user = get_user_model().objects.get(username='mich')
		self.assertTrue(user is not None)

	def test_register_already_exist(self):
		get_user_model().objects.create_user(username='bob')
		request = self.client.post('/auth/register/', {'username': 'bob', 'password': 'ok'})
		self.assertEqual(request.status_code, 400)
