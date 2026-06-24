from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model, authenticate
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user = serializer.create(serializer.validated_data)
                token, _ = Token.objects.get_or_create(user=user)
                
                return Response({
                    "success": True,
                    "message": "Registration successful",
                    "user": UserSerializer(user).data,
                    "token": token.key
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "success": False,
                    "error": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        email_or_username = serializer.validated_data['emailOrUsername']
        password = serializer.validated_data['password']

        # Try to find user by username or email
        user = None
        
        # Check if input is email
        if '@' in email_or_username:
            try:
                user_obj = User.objects.get(email=email_or_username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        else:
            # Try username authentication
            user = authenticate(username=email_or_username, password=password)

        if user is None:
            return Response({
                "success": False,
                "error": "Invalid username/email or password"
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                "success": False,
                "error": "User account is disabled"
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Get or create token
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            "success": True,
            "message": "Login successful",
            "user": UserSerializer(user).data,
            "token": token.key
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Delete the user's token
            if request.auth:
                request.auth.delete()
            return Response({
                "success": True,
                "message": "Logged out successfully"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "success": True,
            "user": UserSerializer(request.user).data
        }, status=status.HTTP_200_OK)