from django.db import models

class ChatMessage(models.Model):
    sender = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField()
    date = models.DateField()
    chat_id = models.CharField(max_length=255)
    media_urls = models.TextField(blank=True, null=True)  # Store as JSON list
    
    def __str__(self):
        return f"{self.sender} to {self.receiver} at {self.timestamp}"
    
    class Meta:
        indexes = [
            models.Index(fields=['sender']),
            models.Index(fields=['receiver']),
            models.Index(fields=['date']),
            models.Index(fields=['chat_id']),
        ]

class MediaFile(models.Model):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
    ]
    
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='media_files')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50, choices=MEDIA_TYPES)
    file_url = models.URLField()
    file_path = models.TextField(blank=True, null=True)  # Local storage path
    downloaded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.file_type}: {self.file_name}"