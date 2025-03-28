from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import QRMenu, MenuItem
from .serializers import BulckSerializerMenuItem, QRMenuSerializer, MenuItemSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, viewsets
from .models import QRMenu
from . import tasks


class CreateMenuView(APIView):


    permission_classes = [IsAuthenticated]

    def post(self, request):
        serz_data = QRMenuSerializer(data=request.data)

        if serz_data.is_valid():
            user = request.user
            menu = QRMenu.objects.create(
                title = serz_data.validated_data['title'],
                description = serz_data.validated_data['description'],
                user=user
            )
            request.session['menu_id'] = menu.id
            return Response(QRMenuSerializer(menu).data, status=status.HTTP_201_CREATED)
        
        return Response({'errors': serz_data.errors, 'message': 'Validation failed.'}, status=status.HTTP_400_BAD_REQUEST)
    


class AddMenuItemView(APIView):


    permission_classes = [IsAuthenticated]

    def post(self, request):
        menu_id = request.session.get('menu_id')
        if menu_id:
            menu = get_object_or_404(QRMenu, id=menu_id)
            if menu.user == request.user:
                        
                serz_data = BulckSerializerMenuItem(data=request.data,
                                            context={'menu':menu, 'request':request})
                if serz_data.is_valid():
                    serz_data.save()
                    
                    return Response({'message':'items saved'}, status=status.HTTP_201_CREATED)
                return Response(serz_data.errors, status=status.HTTP_400_BAD_REQUEST) 
            
            return Response({'detail':'You do not have permission to modify this menu.'},
                                status=status.HTTP_403_FORBIDDEN)
        redirect_url = reverse('home:create_menu')
        return Response({'message':'session has been expired', 'redirect link':redirect_url},
                        status=status.HTTP_308_PERMANENT_REDIRECT)

class ReceiveQRimage(APIView):


    permission_classes = [IsAuthenticated]

    def get(self, request):
        session_id = request.session.get('menu_id')
        if session_id:
            menu = QRMenu.objects.get(id=session_id)
        
            serz_data = QRMenuSerializer(menu)
            qr_image = menu.qr_code
            del request.session['menu_id']
            return Response({'data':serz_data.data, 
                            'image':qr_image.url}, status=status.HTTP_200_OK)
        
        redirect_url = reverse('home:create_menu')
        return Response({'detail':'session has been expired', 'redirect link':redirect_url}
                        , status=status.HTTP_404_NOT_FOUND)



class FetchMenu(APIView):


    permission_classes = [AllowAny]

    def get(self ,request, menu_id):
        menu = get_object_or_404(QRMenu, id=menu_id)
        serz_menu = QRMenuSerializer(menu)
        serz_menu = serz_menu.data

        items = MenuItem.objects.filter(menu=menu)
        items_serializer = MenuItemSerializer(items, many=True)
        items = items_serializer.data

        return Response({
            'menu':serz_menu,
            'items':items
        }, status=status.HTTP_200_OK)



class MenuViewSet(viewsets.ViewSet):

 
    permission_classes = [IsAuthenticated]
    queryset = QRMenu.objects.all()


    def list(self ,request):

        user = request.user
        menus = self.queryset.filter(user=user)
        serz_data = QRMenuSerializer(instance=menus, many=True)
        return Response(serz_data.data, status=status.HTTP_200_OK)



    def retrieve(self, request, pk=None):
     
        menu = get_object_or_404(QRMenu, id=pk)
        serz_data = QRMenuSerializer(instance=menu)
        qr_image = menu.qr_code.url
        return Response({'data':serz_data.data,
                         'image':qr_image}, status=status.HTTP_200_OK)



    def partial_update(self, request, pk):
    
        menu = get_object_or_404(QRMenu, id=pk)
        if menu.user == request.user:

            serz_data = QRMenuSerializer(instance=menu, data=request.data, partial=True)
            if serz_data.is_valid():
                qr_image = str(menu.qr_code)
                tasks.delete_object_tasks(qr_image)
                serz_data.save()
                return Response(serz_data.data, status=status.HTTP_200_OK)
            
            return Response(serz_data.errors, status=status.HTTP_400_BAD_REQUEST)
                
        return Response({'message':'You are only allowed to update your own menus.'},)



    def destroy(self, request, pk):
     
        menu = get_object_or_404(QRMenu, id=pk, user=request.user)
        if menu:
            menu.delete()  
            return Response({'message':'Menu has been deleted'}, status=status.HTTP_200_OK)
        return Response({'message':'menu dose not exist'}, status=status.HTTP_400_BAD_REQUEST)
     


class RemoveItemView(APIView):
    

    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:    
            item = MenuItem.objects.get(id=item_id)
        except MenuItem.DoesNotExist:
            return Response({'message':'Item not found'}, status=status.HTTP_404_NOT_FOUND)


        menu = item.menu
        if menu.user == request.user:
            item.delete()
        
            return Response({'message':'Item has been deleted'}, status=status.HTTP_200_OK)

        return Response({'message':'You do not have permission to modify this menu.'},
                        status=status.HTTP_403_FORBIDDEN)        

class UpdateItemView(APIView):


    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        
        try:
            item = MenuItem.objects.get(id=item_id)
        except MenuItem.DoesNotExist:
            return Response({'message':'item does not exist'}, status=status.HTTP_404_NOT_FOUND)

        menu = item.menu
        if menu.user == request.user:
            serz_data = MenuItemSerializer(instance=item, data=request.data, partial=True)
            if serz_data.is_valid():
                serz_data.save()
                return Response(serz_data.data, status=status.HTTP_200_OK)

            return Response(serz_data.errors, status=status.HTTP_400_BAD_REQUEST)
           
        return Response({'message': 'You do not have permission to modify this menu.'}, status=status.HTTP_403_FORBIDDEN)       



class AddItemView(APIView):
   

    permission_classes = [IsAuthenticated]

    def post(self ,request, menu_id):
        menu = get_object_or_404(QRMenu, id=menu_id)
        if menu.user == request.user:

            serz_data = MenuItemSerializer(data=request.data, context={'menu':menu})
            
            if serz_data.is_valid():
                serz_data.save()
                return Response(serz_data.data, status=status.HTTP_201_CREATED)
            
            return Response(serz_data.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'You do not have permission to modify this menu.'}, status=status.HTTP_403_FORBIDDEN)
    

