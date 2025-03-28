from accounts.models import User
from menu.models import QRMenu, MenuItem
from rest_framework.test import APIClient,APITestCase
from django.urls import reverse
from rest_framework import status
from menu.serializers import QRMenuSerializer



class TestCreateMenu(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('home:create_menu')
        self.user = User.objects.create_user(username='testuser',
                                             phone_number='0123456789',
                                             password='1234')
        self.valid_data = {
            'title':'the menu',
            'description':'a menu just for test'
        }
        self.invalid_data = {
            'title':None,
            'description':'a menu just for test'
        }

    def test_valid_menu_creation(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data=self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.valid_data['title'])
        self.assertEqual(response.data['description'], self.valid_data['description'])
        self.assertIn('id', response.data)

        menu = QRMenu.objects.filter(id=response.data['id'], user=self.user).exists()
        self.assertTrue(menu)


    def test_invalid_creation(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data=self.invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_unauthentication_creation(self):
        response = self.client.post(self.url, data=self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestAddMenuItem(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('home:add_menu_item')
        self.user = User.objects.create_user(username='testuser',
                                             phone_number='011111111',
                                             password='1234')
        
        self.another_user = User.objects.create_user(username='another_user',
                                                     phone_number='0222222222',
                                                     password='1234')
        
        self.menu = QRMenu.objects.create(title='the menu',
                                          description=' a menu for test',
                                          user=self.user)
        
        self.client.force_authenticate(user=self.user)
        session = self.client.session
        session['menu_id'] = self.menu.id
        session.save()

        self.valid_data = {
            "items": [
                {
                    "item": "Pizza",
                    "description": "Delicious cheese pizza",
                    "price": 1500
                },
                {
                    "item": "Pasta",
                    "description": "Creamy Alfredo pasta",
                    "price": 1200
                }
            ]
        }
      
        self.invalid_data = [
            {
                "item": "",
                "description": "No item name",
                "price": -100,
        }
        ]


    def test_success_items_add(self):
        response = self.client.post(self.url, data=self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'items saved')

        items = MenuItem.objects.filter(menu=self.menu)
        self.assertEqual(items.count(), 2)
        self.assertTrue(items.filter(item='Pizza').exists())
        self.assertTrue(items.filter(item='Pasta').exists())

    def test_fail__invalid_items_add(self):
        response = self.client.post(self.url, data=self.invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        items = MenuItem.objects.filter(menu=self.menu)
        self.assertEqual(items.count(), 0)

    def test_unauthrized_add_item(self):
        self.client.force_authenticate(user=self.another_user)
        response = self.client.post(self.url, data=self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to modify this menu.')

    def test_expired_session(self):
        self.client.force_authenticate(user=self.user)
        session = self.client.session
        del session['menu_id']
        session.save()

        response = self.client.post(self.url, data=self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_308_PERMANENT_REDIRECT)
        self.assertEqual(response.data['message'], 'session has been expired')


class TestReceiveQRimage(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('home:get_code')
        self.user = User.objects.create_user(username='testuser',
                                             phone_number='011111111',
                                             password='1234')
        self.client.force_authenticate(user=self.user)

        self.menu = QRMenu.objects.create(title='the menu',
                                          description=' a menu for test',
                                          user=self.user)
    def test_success_get_qrcode(self):
        session = self.client.session
        session['menu_id'] = self.menu.id
        session.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_not_fount_menu(self):

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestFetchMenu(APITestCase):

    def setUp(self):
        self.client = APIClient()
        

        user = User.objects.create_user(username='testuser',
                                             phone_number='011111111',
                                             password='1234')
        self.menu = QRMenu.objects.create(title='the menu',
                                          description=' a menu for test',
                                          user=user)
        self.item1 = MenuItem.objects.create(
            menu=self.menu,              
            item = "Pizza",
            description = "Delicious cheese pizza",
            price = 1500)

        self.item2 = MenuItem.objects.create(
            menu=self.menu,              
            item = "Pasta",
            description = "Creamy Alfredo pasta",
            price = 1200)
     
        self.url = reverse('home:fetch_menu', args=[self.menu.id])
    
    def test_success_fetch_menu(self):

        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['menu']['title'], self.menu.title)
        self.assertEqual(response.data['menu']['id'], self.menu.id)

        items = response.data['items']
        self.assertEqual(len(items), 2)


class TestRemoveItem(APITestCase):

    def setUp(self):
        self.client = APIClient()


        self.user = User.objects.create_user(username='testuser',
                                             phone_number='011111111',
                                             password='1234')
        
        self.other_user = User.objects.create_user(username='otheruser',
                                                   phone_number='0222222222',
                                                   password='1234')
        
        self.menu = QRMenu.objects.create(title='the menu',
                                          description=' a menu for test',
                                          user=self.user)
        self.item = MenuItem.objects.create(
            menu=self.menu,              
            item = "Pizza",
            description = "Delicious cheese pizza",
            price = 1500)
       
        self.valid_url = reverse('home:remove_item', args= [self.item.id])
        self.invalid_url = reverse('home:remove_item', args= [768])
    
    def test_success_delete_item(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.valid_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(MenuItem.objects.filter(id=self.item.id).exists())


    def test_unauthrized_delete_item(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.valid_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'You do not have permission to modify this menu.')
        
    def test_fail_delete_item(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Item not found')


class TestUpdateItem(APITestCase):

    def setUp(self):
        self.client = APIClient()
        
        self.user = User.objects.create_user(username='testuser',
                                             phone_number='011111111',
                                             password='1234')
        
        self.other_user = User.objects.create_user(username='otheruser',
                                                   phone_number='0222222222',
                                                   password='1234')
        
        self.menu = QRMenu.objects.create(title='the menu',
                                          description=' a menu for test',
                                          user=self.user)
        self.item = MenuItem.objects.create(
            menu=self.menu,              
            item = "Pizza",
            description = "Delicious cheese pizza",
            price = 1500)
        
        self.valid_url = reverse('home:update_item', args=[self.item.id])
        self.invalid_url = reverse('home:update_item', args=[863])

    def test_success_update_item(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(self.valid_url, data={'price':'1200'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fail_update_item(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.valid_url, data={'price': None},
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_notfound_update_item(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(self.invalid_url, data=self.valid_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_unauthrized_update_item(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(self.valid_url, data={'price':'1200'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'You do not have permission to modify this menu.')


class TestAdditem(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser',
                                             phone_number='011111111',
                                             password='1234')
        
        self.other_user = User.objects.create_user(username='otheruser',
                                                   phone_number='0222222222',
                                                   password='1234')
        
        self.menu = QRMenu.objects.create(title='the menu',
                                          description=' a menu for test',
                                          user=self.user)
        self.valid_item = {'item':'Pizza',
                           'description':'Special pizza',
                           'price':1200}
        
        self.invalid_data = {'item':None,
                           'description':'Special pizza',
                           'price':''}

        self.valid_url = reverse('home:add_item', args=[self.menu.id])
        self.invalid_url = reverse('home:add_item', args=[235])


    def test_success_add_item(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.valid_url, data=self.valid_item, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_not_found_add_item(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.invalid_url, data=self.valid_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthrized_add_item(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(self.valid_url, data=self.valid_item, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'You do not have permission to modify this menu.')
            
    def test_fail_add_item(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.valid_url, data=self.invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestViewSet(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser',
                                             phone_number='011111111',
                                             password='1234')
        
        self.other_user = User.objects.create_user(username='otheruser',
                                                   phone_number='0222222222',
                                                   password='1234')
        
        self.menu1 = QRMenu.objects.create(title='the menu',
                                          description=' a menu for test',
                                          user=self.user)
        self.menu2 = QRMenu.objects.create(title='seconde menu',
                                          description=' a seconde menu for test',
                                          user=self.user)
        self.other_users_menu = QRMenu.objects.create(title='other menu',
                                          description=' a menu form other user',
                                          user=self.other_user)
        
        self.list_url = reverse('home:menu-list')
        self.retrieve_url = reverse('home:menu-detail', args=[self.menu1.id])
        self.partial_update_url = reverse('home:menu-detail', args=[self.menu1.id])
        self.destroy_url = reverse('home:menu-detail', args=[self.menu1.id])

    def test_list_viewset(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        menus = QRMenu.objects.filter(user=self.user).all()
        serz_data = QRMenuSerializer(menus, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serz_data.data)

    def test_retrieve_viewset(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.retrieve_url)
        menu = QRMenu.objects.get(id=self.menu1.id)
        serz_data = QRMenuSerializer(menu)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data'], serz_data.data)
        self.assertIn('image', response.data)


    def test_partial_update_viewset(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.partial_update_url, data={'title':'updated menu'},
                                     format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'updated menu')

    def test_destroy_viewser(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.destroy_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(QRMenu.objects.filter(id=self.menu1.id).exists())