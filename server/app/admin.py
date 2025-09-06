from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "room_name", "user", "content", "timestamp")
    list_filter = ("room_name", "timestamp", "user")
    search_fields = ("content", "room_name", "user__username")
    ordering = ("-timestamp",)
