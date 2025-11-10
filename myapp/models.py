from django.db import models

# Create your models here.
class SystemMetric(models.Model):
    system_id = models.CharField(max_length=64, unique=True)
    hostname = models.CharField(max_length=128, blank=True)
    cpu = models.FloatField(default=0)
    ram = models.FloatField(default=0)
    disk = models.FloatField(default=0)
    ping = models.FloatField(default=0) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hostname or 'Unknown'} ({self.system_id})"