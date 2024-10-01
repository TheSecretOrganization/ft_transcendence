from django.db import models
from django.contrib.auth import get_user_model

class Pong(models.Model):
    user1 = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, null=True, related_name="user1"
    )
    user2 = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, null=True, related_name="user2"
    )
    score1 = models.PositiveSmallIntegerField()
    score2 = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user1.username} vs {self.user2.username} - {self.score1}:{self.score2}"
