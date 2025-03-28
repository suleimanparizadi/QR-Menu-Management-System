from django.test import TestCase
from accounts.models import User
from menu.models import QRMenu
from django.core.files.storage import default_storage

class TestQRMneu(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             phone_number='011111111',
                                             password='1234')
        
    def test_create_qrmenu(self):
        menu =QRMenu.objects.create(title='the menu',
                                    description = 'a menu for test',
                                    user=self.user)
        self.assertEqual(menu.title, 'the menu')
        self.assertEqual(menu.description, 'a menu for test')
        self.assertTrue(menu.available)
        self.assertIsNotNone(menu.qr_code)
        self.assertTrue(default_storage.exists(menu.qr_code.name))

    
    def test_delete_qrmenu(self):
        menu =QRMenu.objects.create(title='the menu',
                                    description = 'a menu for test',
                                    user=self.user)
        name = menu.qr_code.name
        menu.delete()
        self.assertFalse(default_storage.exists(name))