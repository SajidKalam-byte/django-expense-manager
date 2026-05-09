from django.db import models

class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
