from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    class Meta:
        ordering = ('created',)

    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default='')


admin.site.register(Profile)