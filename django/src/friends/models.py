from django.db import models
from django.db.models import Q, F
from django.core.exceptions import ValidationError
from ft_auth.models import User

class Friend(models.Model):
	class Status(models.IntegerChoices):
		PENDING = 1
		ACCEPTED = 2
		DENIED = 3
		DELETED = 4

	origin = models.ForeignKey(User, models.CASCADE, related_name='origin')
	target = models.ForeignKey(User, models.CASCADE, related_name='target')
	status = models.IntegerField(choices=Status, default=Status.PENDING)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['origin', 'target'], condition=Q(status=1) | Q(status=2), name='unique_friend_request'),
			models.CheckConstraint(check=~Q(origin=F('target')), name='unique_origin_target')
		]

	def clean(self):
		if Friend.objects.filter(origin=self.target, target=self.origin, status__in=[1, 2]).exists():
			raise ValidationError('This request already exist')

	def save(self, *args, **kwargs):
		self.clean()
		super().save(*args, **kwargs)
