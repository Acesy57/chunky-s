from django.db import models
from django.contrib.auth.models import User  

# Create your models here.
class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.message}: {self.user_message} ->{self.bot_response}"

class Webhook(models.Model):
    url = models.URLField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.url
    
class ChatAnalytics(models.Model):
    date = models.DateField(auto_now_add=True)
    total_chats = models.IntegerField(default=0)
    unique_users = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Chat Analytics"


class Intent(models.Model):
    name = models.CharField(max_length=100, unique=True)
    keywords = models.TextField()

    def __str__(self):
        return self.name

class Response(models.Model):
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, related_name='responses')
    text = models.TextField()

    def __str__(self):
         return f"{self.intent.name}: {self.text[:50]}..."