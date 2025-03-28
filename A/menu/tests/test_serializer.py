from django.test import TestCase
from accounts.models import User
from menu.models import QRMenu, MenuItem
from menu.serializers import QRMenuSerializer, MenuItemSerializer, BulckSerializerMenuItem

class TestSerializers(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", phone_number="011111111", password="1234")

        self.menu = QRMenu.objects.create(
            user=self.user,
            title="Test Menu",
            description="A sample description"
        )

        self.item = MenuItem.objects.create(
            menu=self.menu,
            item="Pizza",
            description="Cheese Pizza",
            price=1500
        )

    def test_qr_menu_serializer(self):
        serializer = QRMenuSerializer(instance=self.menu)
        expected_data = {
            'id': self.menu.id,
            'title': self.menu.title,
            'description': self.menu.description,
        }

        self.assertEqual(serializer.data, expected_data)

    def test_menu_item_serializer(self):
        serializer = MenuItemSerializer(instance=self.item)
        expected_data = {
            'id': self.item.id,
            'item': self.item.item,
            'description': self.item.description,
            'price': self.item.price,
        }

        self.assertEqual(serializer.data, expected_data)

    def test_menu_item_serializer_create(self):
        data = {
            'item': "Burger",
            'description': "Delicious beef burger",
            'price': 2000,
        }
        serializer = MenuItemSerializer(data=data, context={'menu': self.menu})
        self.assertTrue(serializer.is_valid())
        new_item = serializer.save()

        self.assertEqual(new_item.item, data['item'])
        self.assertEqual(new_item.description, data['description'])
        self.assertEqual(new_item.price, data['price'])
        self.assertEqual(new_item.menu, self.menu)

    def test_bulk_serializer_menu_item(self):
        data = {
            'items': [
                {'item': "Sushi", 'description': "Fresh sushi", 'price': 3000},
                {'item': "Pasta", 'description': "Creamy pasta", 'price': 2500},
            ]
        }
        serializer = BulckSerializerMenuItem(data=data, context={'menu': self.menu})
        self.assertTrue(serializer.is_valid())
        created_items = serializer.save()

        self.assertEqual(len(created_items), 2)
        self.assertEqual(created_items[0].item, "Sushi")
        self.assertEqual(created_items[1].item, "Pasta")
        self.assertEqual(created_items[0].menu, self.menu)
        self.assertEqual(created_items[1].menu, self.menu)
