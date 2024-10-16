from django.db import models
from django.contrib.auth import get_user_model


class Pong(models.Model):
    user1 = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="user1",
    )
    user2 = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="user2",
    )
    score1 = models.PositiveSmallIntegerField()
    score2 = models.PositiveSmallIntegerField()
    uuid = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user1.username} vs {self.user2.username} - {self.score1}:{self.score2}"


class PongTournament(models.Model):
    name = models.CharField(max_length=255, unique=True)
    winner = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="winner",
    )
    participants = models.ManyToManyField(
        get_user_model(), related_name="tournaments"
    )
    games = models.ManyToManyField(Pong, related_name="tournaments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tournament: {self.name} - Winner: {self.winner}"
