from django.contrib import admin
from .models import PongGame

@admin.register(PongGame)
class PongGameAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'score1', 'score2', 'created_at')
    search_fields = ('user1__username', 'user2__username')
    list_filter = ('created_at',)
