from rest_framework import serializers

from .models import MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    # Returned as an absolute URL so the Flutter app can drop it straight
    # into Image.network(imageUrl) with no extra path building.
    imageUrl = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'imageUrl', 'size', 'price', 'is_available']

    def get_imageUrl(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url
