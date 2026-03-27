from django.contrib import admin
from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'carpark_name', 'carpark_id', 'district', 'created_at')
    list_filter = ('district',)
    search_fields = ('user__username', 'carpark_name', 'carpark_id')
    ordering = ('-created_at',)
