from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import AbstractBaseUser
from .validators import validate_alnum
from .manager import UserManager

class User(AbstractBaseUser):
	username = models.CharField(max_length=15, unique=True, validators=[MinLengthValidator(3), validate_alnum])
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)

	objects = UserManager()

	USERNAME_FIELD = 'username'

	def has_perm(self, perm, obj=None):
		return True

	def has_module_perms(self, perm, obj=None):
		return True

	@property
	def is_staff(self):
		return self.is_admin

class FtOauth(models.Model):
	ft_id = models.PositiveIntegerField()
	login = models.CharField(max_length=15)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
