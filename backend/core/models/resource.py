from django.db import models

from core.models.category import Category


class Resource(models.Model):
    name = models.CharField(max_length=200)
    # PROTECT: a category with resources attached to it shouldn't be
    # deletable from the admin without first reassigning those resources.
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="resources")
    zone = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=30, blank=True)
    hours = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.zone})"
