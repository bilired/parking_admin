from rest_framework import serializers
from .models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = (
            'id', 'carpark_id', 'carpark_name', 'carpark_name_en',
            'district', 'address', 'latitude', 'longitude', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class FavoriteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = (
            'carpark_id', 'carpark_name', 'carpark_name_en',
            'district', 'address', 'latitude', 'longitude'
        )

    def create(self, validated_data):
        user = self.context['request'].user
        favorite, created = Favorite.objects.get_or_create(
            user=user,
            carpark_id=validated_data['carpark_id'],
            defaults=validated_data
        )
        if not created:
            raise serializers.ValidationError({'detail': '已收藏此停車場'})
        return favorite
