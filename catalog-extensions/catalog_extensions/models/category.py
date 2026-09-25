from django.db import models


class CatalogCategory(models.Model):
    key = models.SlugField(
        max_length=100,
        unique=True,
    )
    name = models.CharField(
        max_length=200,
    )
    description = models.TextField(
        blank=True,
    )
    display_order = models.PositiveIntegerField(
        default=0,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    modified = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = (
            "display_order",
            "name",
        )
        verbose_name_plural = "catalog categories"

    def __str__(self):
        return self.name
