import jwt
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status, permissions, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UploadSerializer
from .models import Upload
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

        user_directory = f'uploads/{user.username}'
        os.makedirs(user_directory, exist_ok=True) 

        file_path = os.path.join(user_directory, uploaded_file.name)

        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        file_type = uploaded_file.name.split('.')[-1].lower()

        uploaded_file_record = Upload.objects.create(
            path=file_path,
            type=file_type,
            uploaded_by=user,
            name=file_name
        )

        serializer = UploadSerializer(uploaded_file_record)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class FileListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        token = request.headers.get('Authorization')

        if not token:
            return Response({'error': 'Token is required in Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')

            if not user_id:
                return Response({'error': 'Token is missing user ID'}, status=status.HTTP_401_UNAUTHORIZED)

            user = User.objects.get(id=user_id)
        except Exception as e:
            return Response({'error': f'Invalid or expired token: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

        # Retrieve all uploads for the user
        uploads = Upload.objects.filter(uploaded_by=user)
        serializer = UploadSerializer(uploads, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class FileUpdateView(APIView):

    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser]

    def put(self, request, upload_id):

        token = request.headers.get('Authorization')

        if not token:
            return Response({'error': 'Token is required in Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')

            if not user_id:
                return Response({'error': 'Token is missing user ID'}, status=status.HTTP_401_UNAUTHORIZED)

            user = User.objects.get(id=user_id)
        except Exception as e:
            return Response({'error': f'Invalid or expired token: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

        # Get the upload to be updated
        try:
            upload = Upload.objects.get(id=upload_id, uploaded_by=user)
        except Upload.DoesNotExist:
            return Response({'error': 'File not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)

        # Get new file data
        new_file = request.FILES.get('file')
        new_name = request.data.get('name')

        if not new_file or not new_name:
            return Response({'error': 'New file and name are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Remove the old file from storage
        if os.path.exists(upload.path):
            os.remove(upload.path)

        # Save new file in the same directory
        user_directory = f'uploads/{user.username}'
        os.makedirs(user_directory, exist_ok=True)
        new_file_path = os.path.join(user_directory, new_file.name)

        with open(new_file_path, 'wb+') as destination:
            for chunk in new_file.chunks():
                destination.write(chunk)

        # Update upload record in the database
        upload.path = new_file_path
        upload.type = new_file.name.split('.')[-1].lower()
        upload.name = new_name
        upload.save()

        serializer = UploadSerializer(upload)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class FileDeleteView(APIView):
    """
    API endpoint for deleting an uploaded file.
    Requires a valid JWT token in the request headers.
    """
    permission_classes = [permissions.AllowAny]

    def delete(self, request, upload_id):
        """
        Deletes an existing uploaded file.
        The token must be in the Authorization header.
        """
        token = request.headers.get('Authorization')

        if not token:
            return Response({'error': 'Token is required in Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')

            if not user_id:
                return Response({'error': 'Token is missing user ID'}, status=status.HTTP_401_UNAUTHORIZED)

            user = User.objects.get(id=user_id)
        except Exception as e:
            return Response({'error': f'Invalid or expired token: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

        # Get the upload to be deleted
        try:
            upload = Upload.objects.get(id=upload_id, uploaded_by=user)
        except Upload.DoesNotExist:
            return Response({'error': 'File not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)

        # Remove the file from storage
        if os.path.exists(upload.path):
            os.remove(upload.path)

        # Delete the record from the database
        upload.delete()

        return Response({'message': 'File deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class FileRetrieveView(APIView):
    """
    API endpoint for retrieving a specific uploaded file's details.
    Requires a valid JWT token in the request headers.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, upload_id):
        """
        Fetches details of a specific uploaded file.
        The token must be in the Authorization header.
        """
        token = request.headers.get('Authorization')

        if not token:
            return Response({'error': 'Token is required in Authorization header'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')

            if not user_id:
                return Response({'error': 'Token is missing user ID'}, status=status.HTTP_401_UNAUTHORIZED)

            user = User.objects.get(id=user_id)
        except Exception as e:
            return Response({'error': f'Invalid or expired token: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

        # Retrieve the specific upload
        try:
            upload = Upload.objects.get(id=upload_id, uploaded_by=user)
        except Upload.DoesNotExist:
            return Response({'error': 'File not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UploadSerializer(upload)
        return Response(serializer.data, status=status.HTTP_200_OK)