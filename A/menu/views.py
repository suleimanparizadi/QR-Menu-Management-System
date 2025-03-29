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
    """
    API endpoint for creating a QR menu.

    This class provides functionality for authenticated users to create a new QR menu associated with their account. 
    It accepts menu details (title and description) in the request, validates the input, and saves the menu to the database.
    The created menu ID is stored in the user's session for future reference.

    Permissions:
        - IsAuthenticated: Only authenticated users can access this endpoint.

    HTTP Methods:
        - POST: Creates a new QR menu.

    Responses:
        - 201 Created: The menu was successfully created.
        - 400 Bad Request: Validation failed due to invalid input data.
    """
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
    """
    API endpoint for adding items to a menu.

    This view allows authenticated users to add multiple items to a QR menu.
    The menu must exist in the user's session and belong to the authenticated user. 
    Bulk item creation is performed using the `BulckSerializerMenuItem`. If the 
    session has expired, the user is redirected to the menu creation page.

    Permissions:
        - IsAuthenticated: Only authenticated users can access this endpoint.

    HTTP Methods:
        - POST: Adds items to a menu.

    Behavior:
        1. Checks the session for the `menu_id`.
        2. Validates that the menu belongs to the authenticated user.
        3. Uses the `BulckSerializerMenuItem` for bulk creation of menu items.
        4. Responds with a success message upon successful creation or error details upon failure.

    Responses:
        - 201 Created: Items were successfully added to the menu.
        - 400 Bad Request: Validation errors occurred while processing the input.
        - 403 Forbidden: The authenticated user does not have permission to modify the menu.
        - 308 Permanent Redirect: The user's session has expired and they need to create a new menu.
    """
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
    """
    API endpoint for retrieving the QR menu image and its details.

    This view allows authenticated users to retrieve the details and QR code image 
    of a menu stored in the user's session. Once the menu data is retrieved, the 
    session entry for the menu ID is deleted. If the session has expired or the menu 
    ID is not found, the user is redirected to the menu creation page.

    Permissions:
        - IsAuthenticated: Only authenticated users can access this endpoint.

    HTTP Methods:
        - GET: Fetches menu details and QR code image.

    Responses:
        - 200 OK: Returns the menu details and QR code image URL if the session ID is valid.
        - 404 Not Found: Indicates that the session has expired and provides a redirect link to create a new menu.
    """
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
    """
    API endpoint for fetching menu details and its items.

    This view allows any user (authenticated or unauthenticated) to retrieve the details of a 
    specific menu along with all items associated with that menu. The menu and items are serialized 
    into JSON format using the `QRMenuSerializer` and `MenuItemSerializer`, respectively.

    Permissions:
        - AllowAny: This endpoint is accessible to all users, regardless of authentication status.

    HTTP Methods:
        - GET: Fetches menu details and associated items.

    Args:
        menu_id (int): The primary key of the menu to fetch.

    Behavior:
        1. Retrieves the menu instance using `menu_id`.
        2. Serializes the menu and its associated items using the appropriate serializers.
        3. Returns the serialized data in the response.

    Responses:
        - 200 OK: Successfully fetched the menu details and items.
        - 404 Not Found: The menu does not exist.
    """
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
    """
    API endpoint for managing QR menus.

    This ViewSet allows authenticated users to perform CRUD operations on their QR menus. 
    Users can list all their menus, retrieve details of a specific menu along with its QR code, 
    partially update a menu, or delete a menu. All operations ensure that users only have access 
    to the menus they own.

    Permissions:
        - IsAuthenticated: Only logged-in users can access this ViewSet.

    HTTP Methods:
        - GET (list): Retrieves all menus owned by the authenticated user.
        - GET (retrieve): Fetches the details of a specific menu and its QR code.
        - PATCH (partial_update): Partially updates the details of a specific menu.
        - DELETE (destroy): Deletes a specific menu.

    Methods:
        list(request):
            Retrieves a list of all menus associated with the authenticated user.

        retrieve(request, pk):
            Retrieves the details of a specific menu identified by its primary key, 
            along with the QR code image URL.

        partial_update(request, pk):
            Partially updates the details of a specific menu, provided it belongs to 
            the authenticated user. Also deletes and regenerates the associated QR code.

        destroy(request, pk):
            Deletes a specific menu if it belongs to the authenticated user.

    Responses:
        - 200 OK: Successfully retrieves or updates a menu.
        - 400 Bad Request: Validation errors occurred during the update.
        - 403 Forbidden: The user does not have permission to access or modify the menu.
        - 404 Not Found: The menu does not exist.
    """
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
    """
    API endpoint for removing an item from a menu.

    This view allows authenticated users to delete a specific menu item by providing the item's ID.
    The endpoint ensures that the menu associated with the item belongs to the requesting user 
    before allowing deletion. If the user does not have the required permissions, an error message 
    is returned.

    Permissions:
        - IsAuthenticated: Only logged-in users can access this endpoint.

    HTTP Methods:
        - DELETE: Deletes a specific menu item.

    Behavior:
        1. Checks if the item exists using its ID.
        2. Verifies that the requesting user is the owner of the menu associated with the item.
        3. Deletes the item if the user has permission.

    Responses:
        - 200 OK: The item was successfully deleted.
        - 403 Forbidden: The user does not have permission to modify the menu.
        - 404 Not Found: The item does not exist.
    """

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
    """
    API endpoint for updating a menu item.

    This view allows authenticated users to update details of a specific menu item. 
    Users can partially update the fields of a menu item, provided they own the menu 
    associated with the item. Validation is performed using the `MenuItemSerializer`.

    Permissions:
        - IsAuthenticated: Only logged-in users can access this endpoint.

    HTTP Methods:
        - PATCH: Partially updates the specified menu item.

    Behavior:
        1. Checks if the item exists using the provided `item_id`.
        2. Verifies that the requesting user is the owner of the menu associated with the item.
        3. Validates the input data using the `MenuItemSerializer`.
        4. Saves the updated data if validation is successful.

    Responses:
        - 200 OK: The item was successfully updated.
        - 400 Bad Request: Validation errors occurred while processing the input.
        - 403 Forbidden: The user does not have permission to modify the menu.
        - 404 Not Found: The item does not exist.
    """
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
    """
    API endpoint for adding an item to a menu.

    This view allows authenticated users to add a new item to a specific menu. 
    The menu must belong to the authenticated user, and the input data for the new 
    item is validated using the `MenuItemSerializer`. If the menu does not belong to 
    the user, an appropriate error response is returned.

    Permissions:
        - IsAuthenticated: Only logged-in users can access this endpoint.

    HTTP Methods:
        - POST: Creates a new menu item.

    Behavior:
        1. Retrieves the menu specified by `menu_id` from the database.
        2. Ensures the menu belongs to the authenticated user.
        3. Validates the input data for the menu item.
        4. Saves the new menu item to the database if validation is successful.

    Responses:
        - 201 Created: The menu item was successfully created.
        - 400 Bad Request: Validation errors occurred while processing the input.
        - 403 Forbidden: The user does not have permission to modify the menu.
        - 404 Not Found: The specified menu does not exist.
    """
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
    

