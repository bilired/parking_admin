from django.conf import settings
from django.db import models


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    carpark_id = models.CharField(max_length=50)
    carpark_name = models.CharField(max_length=200)
    carpark_name_en = models.CharField(max_length=200, blank=True)
    district = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=500, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favorites'
        unique_together = ('user', 'carpark_id')
        ordering = ('-created_at',)
        verbose_name = '收藏'
        verbose_name_plural = '收藏'

    def __str__(self):
        return f'{self.user.username} - {self.carpark_name}'
