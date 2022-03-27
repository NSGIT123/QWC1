from django.db import models
from django.contrib.auth.models import User

class communities(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    community = models.CharField(max_length=255, blank=True, null=True, unique = True)
    predictions = models.TextField(null=True, blank=False)

    def __str__(self):
        return self.user.get_full_name()
