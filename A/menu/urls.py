from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'home'
urlpatterns = [
    path('menu/create/', views.CreateMenuView.as_view(), name='create_menu'),
    path('menu/items/', views.AddMenuItemView.as_view(), name='add_menu_item'),
    path('menu/get_menu/', views.ReceiveQRimage.as_view(), name='get_code'),
    path('menu/fetch/<int:menu_id>', views.FetchMenu.as_view(), name='fetch_menu'),    
    path('item/delete/<int:item_id>', views.RemoveItemView.as_view(), name='remove_item'),
    path('item/update/<int:item_id>/', views.UpdateItemView.as_view(), name='update_item'),
    path('item/add/<int:menu_id>/', views.AddItemView.as_view(), name='add_item'),
]

router = routers.SimpleRouter()

router.register('menu', views.MenuViewSet, basename='menu')
urlpatterns += router.urls
