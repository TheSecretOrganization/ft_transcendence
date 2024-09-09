from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):

	def create_user(self, username, password=None):
		if not username:
			raise TypeError(_('No username provided'))
		user = self.model(username=username)
		user.set_password(password)
		user.save()
		return user

	def create_superuser(self, username, password):
		if not username:
			raise TypeError(_('No username provided'))
		if not password:
			raise TypeError(_('No password provided'))
		user = self.model(username=username)
		user.set_password(password)
		user.is_admin = True
		user.save()
		return user
