from django.db import models

# Create your models here.


class UserActivity(models.Model):
    username = models.CharField(max_length=100)
    event_type = models.CharField(max_length=100)
    source_ip = models.GenericIPAddressField()
    destination_ip = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    risk_score = models.FloatField(default=0.0)
    is_suspicious = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} - {self.event_type}"