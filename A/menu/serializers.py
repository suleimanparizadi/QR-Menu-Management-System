from .models import QRMenu, MenuItem
from rest_framework import serializers



class QRMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRMenu
        fields = [
            'id','title', 'description'
        ]



class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = [
          'id', 'item', 'description', 'price'
        ]

    def create(self, validated_data):
        menu = self.context.get('menu')
        return MenuItem.objects.create(menu=menu, **validated_data)

class BulckSerializerMenuItem(serializers.Serializer):
    
    items = MenuItemSerializer(many=True)

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        menu = self.context.get('menu')

        menu_items = [MenuItem(menu=menu, **item) for item in items_data ]
        return MenuItem.objects.bulk_create(menu_items)
