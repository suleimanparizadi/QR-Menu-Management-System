import random
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .models import User, OTPcode
from . import serializer
from rest_framework.response import Response
from rest_framework import status, permissions
from utils import send_otp_code
from django.urls import reverse
from rest_framework.authtoken.models import Token


class UserRegisterView(APIView):
    
    """
    Handles user registration by validating user input, saving the data to a session,
    generating a one-time password (OTP), and sending the OTP to the user's phone number.

    Methods:
        post(request):
            - Validates the incoming user registration data using `UserSerializer`.
            - Stores the validated data (`username`, `phone_number`, `password`) in a session.
            - Generates a random 4-digit OTP.
            - Creates an OTPcode instance to store the generated code and the user's phone number.
            - Sends the OTP to the provided phone number using the `send_otp_code` function.
            - Returns a 200 OK response with a success message if the data is valid.
            - Returns a 400 BAD REQUEST response with validation errors if the data is invalid.

    Permission Classes:
        - AllowAny: No authentication or permission is required to access this view.

    Expected Request Format:
        {
            "username": "string",
            "phone_number": "string",
            "password": "string",
            "password2": "string"  # Used for password confirmation
        }

    Responses:
        - 200 OK: {'detail': 'user will receive a code'}
        - 400 BAD REQUEST: {validation_errors}
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serz_data = serializer.UserSerializer(data=request.data)
        if serz_data.is_valid():

            request.session['user_register_session'] = {
                'username':serz_data.validated_data['username'],
                'phone_number':serz_data.validated_data['phone_number'],
                'password':serz_data.validated_data['password']
            }
            random_code = random.randint(1000, 9999)
            phone_number=serz_data.validated_data['phone_number']
            OTPcode.objects.create(
                phone_number=phone_number,
                code = random_code)
            send_otp_code(phone_number, random_code)
            return Response({'detail':'user will receive a code'}, status=status.HTTP_200_OK)
        
        return Response(serz_data.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UserPhoneVerfiy(APIView):

    """
    API endpoint for verifying the OTP code sent to the user's phone number 
    and completing the user registration process.

    This view validates the OTP code provided by the user and, if the code is 
    correct, creates a new user using the information stored in the session. 
    If the session has expired or the code is incorrect, appropriate error responses 
    are returned.

    Permissions:
        - AllowAny: No authentication or authorization is required.

    HTTP Methods:
        - POST: Validate the OTP code and register the user if valid.

    Behavior:
        1. Checks for a valid user registration session (user_register_session) 
           in the request session.
        2. Validates the provided OTP code against the code stored for the user's 
           phone number.
        3. Creates a new user using the details stored in the session and deletes 
           the OTP code upon successful validation.
        4. Returns a response with a token for the registered user if the 
           verification is successful.
        5. Handles errors such as invalid/expired OTP codes or missing session data.

    Responses:
        - 201 Created: OTP verified successfully, and user has been registered.
        - 400 Bad Request: The OTP code is invalid or errors in the serializer.
        - 308 Permanent Redirect: Session expired; prompts the user to restart the 
          registration process.
        - 404 Not Found: The OTP code does not exist.

    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_session = request.session.get('user_register_session')
        if user_session:

            user_phone = user_session['phone_number']
            serz_data = serializer.OTPserializer(data=request.data)
            
            if serz_data.is_valid():
                user_code = OTPcode.objects.get(phone_number=user_phone)
            
                if user_code.code == serz_data.validated_data['code']:
                    user = User.objects.create_user(
                        phone_number=user_session['phone_number'],
                        username=user_session['username'],
                        password=user_session['password']
                    )
                    request.session.delete()
                    user_code.delete()
                    token, _ = Token.objects.get_or_create(user=user)

                    return Response({'detail':'SignUp successfully', 'token':token.key}, status=status.HTTP_201_CREATED)
                
                return Response({'detail':'the code is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(serz_data.errors, status=status.HTTP_400_BAD_REQUEST)
        
        redirect_url = reverse('accounts:user_register')
        return Response({'detail':'session is expired redirect to user_register',
                          'redirect link':redirect_url}, status=status.HTTP_308_PERMANENT_REDIRECT)
    


class UserLoginPassword(APIView):

    """
    API endpoint for authenticating users using either a username or phone number 
    (identifier) and password.

    This view processes the login credentials provided by the user, authenticates them, 
    and returns a token for successful logins. The identifier can be either the user's 
    username or their phone number. If authentication fails, appropriate error responses 
    are returned.

    Permissions:
        - AllowAny: No authentication or authorization is required to access this endpoint.

    HTTP Methods:
        - POST: Authenticate the user and return an authorization token.

    Behavior:
        1. Validates the input data using the `UserloginPasswordSerializer`.
        2. Authenticates the user using the `authenticate` method with the provided 
           identifier and password.
        3. Generates a token for the authenticated user and returns it upon successful login.
        4. Handles errors such as incorrect username/password or invalid input data.

    Responses:
        - 200 OK: Authentication successful; returns the user's token.
        - 400 Bad Request: Invalid credentials or validation errors.
        - 401 Unauthorized: Occurs if authentication fails due to incorrect username or password.

    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serz_data = serializer.UserloginPasswordSerializer(data=request.data)
        if serz_data.is_valid():

            identifier = serz_data.validated_data.get('identifier')
            password = serz_data.validated_data.get('password')
            user = authenticate(request, identifier=identifier, password=password)
            if user:
                
                token, _ = Token.objects.get_or_create(user=user)
                
                return Response({'token':token.key}, status=status.HTTP_200_OK)
            
            return Response({'detail':'username or password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serz_data.errors, status=status.HTTP_400_BAD_REQUEST)



class UserLoginSendCode(APIView):
    
    """
    API endpoint for requesting an OTP (One-Time Password) code for login.

    This view allows users to request an OTP code by providing their phone number. 
    The OTP serves as an alternative login method for users who may not remember 
    their passwords. If the provided phone number is associated with an existing user, 
    an OTP code is generated and sent to the user via the specified communication channel 
    (SMS). The OTP is stored temporarily and used for subsequent authentication.

    Permissions:
        - AllowAny: No authentication or authorization is required to access this endpoint.

    HTTP Methods:
        - POST: Validate the phone number and send an OTP code if valid.

    Behavior:
        1. Validates the provided phone number using `UserLoginSendCodeSerializer`.
        2. Checks if a user with the provided phone number exists in the database.
        3. Generates a random 4-digit OTP code and stores it in the `OTPcode` model.
        4. Sends the OTP code to the user via the `send_otp_code` function.
        5. Saves the phone number in the session for use in subsequent steps.
        6. Redirects users without an existing account to the registration endpoint.

    Responses:
        - 200 OK: OTP code generated and sent successfully.
        - 308 Permanent Redirect: Phone number not found; user needs to register.
        - 400 Bad Request: Validation errors in the input data.

    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serz_date = serializer.UserLoginSendCodeSerializer(data=request.data)
        if serz_date.is_valid():
            
            user_phone = serz_date.validated_data.get('phone_number')
            user = User.objects.filter(phone_number=user_phone).exists()
            if user:
               
                random_code = random.randint(1000,9999)
                OTPcode.objects.create(
                    phone_number=user_phone,
                    code=random_code
                )
                send_otp_code(user_phone, random_code)
                request.session['user_phone_number'] = {
                    'user_phone':user_phone
                }

                return Response({'detail':'user will receive a code'}, status=status.HTTP_200_OK)
            
            redirect_url = reverse('accounts:user_register')
            return Response({'detail':'user not singup', 'redirect_url':redirect_url}, status=status.HTTP_308_PERMANENT_REDIRECT)
        
        return Response(serz_date.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UserLoginReceiveCode(APIView):

    """
    API endpoint for verifying an OTP (One-Time Password) code sent to the user's phone number
    and completing the login process.

    This view allows users to submit an OTP code for authentication. If the OTP code matches 
    the one sent to the user's phone number, the user is authenticated, and a token is generated 
    for subsequent API requests. If the OTP is incorrect, expired, or the session has expired, 
    appropriate error responses are returned.

    Permissions:
        - AllowAny: No authentication or authorization is required to access this endpoint.

    HTTP Methods:
        - POST: Verify the OTP code and authenticate the user.

    Behavior:
        1. Validates the provided OTP code using `UserLoginReceiveCodeSerializer`.
        2. Checks if there is a valid session containing the phone number.
        3. Verifies the submitted OTP against the stored OTP code for the user's phone number.
        4. Authenticates the user and generates an authentication token upon success.
        5. Cleans up session data and deletes the OTP code after successful login.
        6. Handles errors such as expired sessions, invalid OTP codes, or missing session data.

    Responses:
        - 200 OK: OTP verified successfully; user is authenticated and a token is provided.
        - 400 Bad Request: Invalid OTP code or validation errors.
        - 308 Permanent Redirect: Session expired; prompts the user to restart the login process.

    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serz_data = serializer.UserLoginReceiveCodeSerializer(data=request.data)
        if serz_data.is_valid():
           

            code = serz_data.validated_data.get('code')
            user_session = request.session.get('user_phone_number')
            if user_session:
                
                user_phone = user_session.get('user_phone')
                user_code = OTPcode.objects.get(phone_number=user_phone)
                if code == user_code.code:

                    user = get_object_or_404(User, phone_number=user_phone)
                    token, _ = Token.objects.get_or_create(user=user)
                    request.session.delete()
                    user_code.delete()
                    
                    return Response({'token':token.key}, status=status.HTTP_200_OK)
                
                return Response({'detail':'Invalid or expired code'})
            
            redirect_url = reverse('accounts:logine_send_code')
            return Response({'detail':'Session expired redirect to logine_send_code',
                             'redirect_url':redirect_url}, status=status.HTTP_308_PERMANENT_REDIRECT)
        
        return Response(serz_data.errors, status=status.HTTP_400_BAD_REQUEST)



class UserLogoutView(APIView):

    """
    API endpoint for logging out an authenticated user.

    This view invalidates the user's authentication token, effectively logging them out. 
    It requires the user to be authenticated before accessing the endpoint. If the token 
    exists, it is deleted, and a confirmation message is returned. If the token does not 
    exist, an error response is provided.

    Permissions:
        - IsAuthenticated: The user must be logged in to access this endpoint.

    HTTP Methods:
        - POST: Invalidate the authentication token and log the user out.

    Behavior:
        1. Retrieves the user's token using the `Token` model and their authentication details.
        2. Deletes the token, logging the user out.
        3. Returns appropriate messages and HTTP status codes based on whether the token exists.

    Responses:
        - 200 OK: User successfully logged out.
        - 404 Not Found: User is not logged in (token does not exist).
        """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token, _ = Token.objects.get(user=request.user)
        if token:
            del token
            return Response({'detail':'user has been loged out'}, status=status.HTTP_200_OK)
        
        return Response({'detail':'user not loged in'}, status=status.HTTP_404_NOT_FOUND)


class UserUpdateProfile(APIView):

    """
    API endpoint for updating a user's profile and password.

    This view allows authenticated users to update their own profile information, including 
    the option to change their password. Partial updates are supported, meaning users can 
    provide only the fields they wish to update. If the user attempts to update another user's 
    profile, the request is denied with an appropriate error response.

    Permissions:
        - IsAuthenticated: The user must be logged in to access this endpoint.

    HTTP Methods:
        - PATCH: Partially update the user's profile with the provided data.

    Behavior:
        1. Retrieves the user instance based on the provided primary key (`id`).
        2. Ensures that the authenticated user can only update their own profile.
        3. Uses `UserSerializer` to validate and serialize the input data for the user instance.
        4. Saves the updated data, including changes to the user's password if provided.
        5. Returns appropriate responses based on the success or failure of the update.

    Responses:
        - 200 OK: Profile updated successfully; returns the updated user data.
        - 400 Bad Request: Validation errors in the provided data.
        - 403 Forbidden: User attempts to update another user's profile.
        - 404 Not Found: User with the specified ID does not exist.

    """



    permission_classes = [permissions.IsAuthenticated]

    def patch(self ,request, pk):
        user = get_object_or_404(User, id=pk)
        if user == request.user:
            serz_data = serializer.UserSerializer(instance=user,
                                                data=request.data, partial=True)
            
            if serz_data.is_valid():
                serz_data.save()
                return Response({'data':serz_data.data, 'detail':'user updated'},
                                status=status.HTTP_200_OK)
                
            return Response(serz_data.errors, status=status.HTTP_400_BAD_REQUEST)
       
        return Response({'detail':'user can onley change thier own profile'}, status=status.HTTP_403_FORBIDDEN)
    