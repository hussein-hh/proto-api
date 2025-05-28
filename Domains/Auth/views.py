from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    SignupSerializer,
    LoginSerializer,
)
from django.conf import settings
from django.contrib.auth import get_user_model
import jwt
from django.utils.timezone import now


def generate_jwt_token(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

User = get_user_model()

def get_user_from_token(token):
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get("user_id")
        if not user_id:
            return None, "Token missing user_id."
        user = User.objects.get(id=user_id)
        return user, None
    except Exception as e:
        return None, f"Invalid or expired token: {str(e)}"


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request,
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )

            if user:
                first_login = user.last_login is None
                user.last_login = now()
                user.save()
                tokens = generate_jwt_token(user)
                return Response({
                    'message': 'Login successful!',
                    'access': tokens['access'],
                    'refresh': tokens['refresh'],
                    'first_login': first_login,
                }, status=status.HTTP_200_OK)

            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmailAPIView(APIView):
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required."}, status=status.HTTP_401_UNAUTHORIZED)

        user, error = get_user_from_token(token)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        new_email = request.data.get("new_email")
        current_password = request.data.get("current_password")
        if not new_email or not current_password:
            return Response(
                {"error": "Both new_email and current_password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(current_password):
            return Response({"error": "Incorrect password."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=new_email).exists():
            return Response({"error": "This email is already in use."}, status=status.HTTP_400_BAD_REQUEST)

        user.email = new_email
        user.save()
        return Response({"message": "Email changed successfully!"}, status=status.HTTP_200_OK)


class ChangePasswordAPIView(APIView):
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required."}, status=status.HTTP_401_UNAUTHORIZED)

        user, error = get_user_from_token(token)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not old_password or not new_password:
            return Response(
                {"error": "Both old_password and new_password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(old_password):
            return Response({"error": "Wrong current password."}, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 8:
            return Response({"error": "New password must be at least 8 characters."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password updated successfully!"}, status=status.HTTP_200_OK)