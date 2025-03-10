import jwt
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status, permissions, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CreateUploadSerializer
from .models import CreateUpload
import os

class FileUploadView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser]

    def post(self, request):
        token = request.data.get('token')

        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')  

            if not user_id:
                return Response({'error': 'Token is missing user ID'}, status=status.HTTP_401_UNAUTHORIZED)

            user = User.objects.get(id=user_id)
        except Exception as e:
            return Response({'error': f'Invalid or expired token: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

        uploaded_file = request.FILES.get('file')
        file_name = request.data.get('name')

        if not uploaded_file or not file_name:
            return Response({'error': 'File and name are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure directory exists
        user_directory = f'uploads/{user.username}'
        os.makedirs(user_directory, exist_ok=True)  # Create directory if it doesn't exist

        file_path = os.path.join(user_directory, uploaded_file.name)

        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        file_type = uploaded_file.name.split('.')[-1].lower()

        uploaded_file_record = CreateUpload.objects.create(
            path=file_path,
            type=file_type,
            uploaded_by=user,
            name=file_name
        )

        serializer = CreateUploadSerializer(uploaded_file_record)

        return Response(serializer.data, status=status.HTTP_201_CREATED)