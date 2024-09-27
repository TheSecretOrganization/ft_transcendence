from django.db import models
from django.core.exceptions import ValidationError
from ft_auth.models import User

class Friend(models.Model):
	class Status(models.IntegerChoices):
		PENDING = 1
		ACCEPTED = 2
		DENIED = 3

	origin = models.ForeignKey(User, models.CASCADE, related_name='origin')
	target = models.ForeignKey(User, models.CASCADE, related_name='target')
	status = models.IntegerField(choices=Status, default=Status.PENDING)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['origin', 'target'], name='unique_friend_request'),
			models.CheckConstraint(check=~models.Q(origin=models.F('target')), name='unique_origin_target')
		]

	def clean(self):
		if Friend.objects.filter(origin=self.target, target=self.origin).exists():
			raise ValidationError('This request already exist')

	def save(self, *args, **kwargs):
		self.clean()
		super().save(*args, **kwargs)
