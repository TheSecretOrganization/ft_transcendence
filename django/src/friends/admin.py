from django.contrib import admin
from .models import Friend

@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
	list_display = ('origin', 'target', 'status', 'created_at', 'updated_at')
	search_fields = ('origin', 'target')
	list_filter = ('created_at', 'updated_at', 'status')
