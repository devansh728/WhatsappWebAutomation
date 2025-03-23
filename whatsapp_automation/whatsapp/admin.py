from django.contrib import admin
from .models import ChatMessage, MediaFile

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'date', 'timestamp', 'message')
    list_filter = ('sender', 'receiver', 'date')
    search_fields = ('sender', 'receiver', 'message')
    date_hierarchy = 'date'

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'file_type', 'downloaded', 'created_at')
    list_filter = ('file_type', 'downloaded')
    search_fields = ('file_name',)
    date_hierarchy = 'created_at'
