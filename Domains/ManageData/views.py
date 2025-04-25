import re
import jwt
from pathlib import Path
from datetime import datetime
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status, permissions, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UploadSerializer
from .models import Upload
from Domains.Onboard.models import Business, Page
from django.http import HttpResponse, FileResponse
import mimetypes
from django.core.cache import cache

User = get_user_model()


def slugify(text):
    """Simple function to convert text into a safe format for folder names."""
    return re.sub(r'[\W_]+', '_', text).strip('_').lower()


def error_response(message, status_code):
    """Helper function to create response objects for better readability."""
    return Response(message, status=status_code)


class FileUploadView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser]

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return error_response({'error': 'Token is required'}, status.HTTP_401_UNAUTHORIZED)
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            if not user_id:
                return error_response({'error': 'Token is missing user ID'}, status.HTTP_401_UNAUTHORIZED)
            user = User.objects.get(id=user_id)
        except Exception as e:
            return error_response({'error': f'Invalid or expired token: {str(e)}'}, status.HTTP_401_UNAUTHORIZED)

        uploaded_file = request.FILES.get('file')
        file_name = request.data.get('name')
        page_id = request.data.get('page_id')  

        if not uploaded_file or not file_name or not page_id:
            return error_response({'error': 'File, name, and page_id are required :()'}, status.HTTP_400_BAD_REQUEST)

        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return error_response({'error': 'Page not found'}, status.HTTP_400_BAD_REQUEST)

        try:
            business = Business.objects.get(user=user)
        except Business.DoesNotExist:
            return error_response({'error': 'Business not found for user'}, status.HTTP_404_NOT_FOUND)

        business_type_slug = slugify(business.category)
        business_name = business.name
        business_id = business.id
        user_id_str = str(user.id)

        user_directory = Path("uploads") / business_type_slug / str(business_id) / user_id_str
        user_directory.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = f"{timestamp}_{business_name}_{business_id}_{"user_name"}_{user_id_str}_{file_name}"
        file_path = user_directory / new_filename

        with file_path.open('wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        file_type = uploaded_file.name.split('.')[-1].lower()

        uploaded_file_record = Upload.objects.create(
            path=str(file_path),
            type=file_type,
            uploaded_by=user,
            name=new_filename,
            references_page=page  
        )
        cache.delete(f"summarizer_output_user_{user.id}")

        serializer = UploadSerializer(uploaded_file_record)
        return error_response(serializer.data, status.HTTP_201_CREATED)


class FileListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        token = request.headers.get('Authorization')
        if not token:
            return error_response({'error': 'Token is required in Authorization header'}, status.HTTP_401_UNAUTHORIZED)
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            if not user_id:
                return error_response({'error': 'Token is missing user ID'}, status.HTTP_401_UNAUTHORIZED)
            user = User.objects.get(id=user_id)
        except Exception as e:
            return error_response({'error': f'Invalid or expired token: {str(e)}'}, status.HTTP_401_UNAUTHORIZED)

        uploads = Upload.objects.filter(uploaded_by=user)
        serializer = UploadSerializer(uploads, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FileUpdateView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser]

    def put(self, request, upload_id):
        token = request.headers.get('Authorization')
        if not token:
            return error_response({'error': 'Token is required in Authorization header'}, status.HTTP_401_UNAUTHORIZED)
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            if not user_id:
                return error_response({'error': 'Token is missing user ID'}, status.HTTP_401_UNAUTHORIZED)
            user = User.objects.get(id=user_id)
        except Exception as e:
            return error_response({'error': f'Invalid or expired token: {str(e)}'}, status.HTTP_401_UNAUTHORIZED)

        try:
            upload = Upload.objects.get(id=upload_id, uploaded_by=user)
        except Upload.DoesNotExist:
            return error_response({'error': 'File not found or unauthorized'}, status.HTTP_404_NOT_FOUND)

        new_file = request.FILES.get('file')
        new_name = request.data.get('name')
        new_page_id = request.data.get('page_id') 

        if not new_file or not new_name:
            return error_response({'error': 'New file and name are required'}, status.HTTP_400_BAD_REQUEST)

        old_file_path = Path(upload.path)
        if old_file_path.exists():
            old_file_path.unlink()

        try:
            business = Business.objects.get(user=user)
        except Business.DoesNotExist:
            return error_response({'error': 'Business not found for user'}, status.HTTP_404_NOT_FOUND)

        business_type_slug = slugify(business.category)
        business_name = business.name
        business_id = business.id
        user_id_str = str(user.id)

        user_directory = Path("uploads") / business_type_slug / str(business_id) / user_id_str
        user_directory.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = f"{timestamp}_{business_name}_{business_id}_{user.username}_{user_id_str}_{new_name}"
        new_file_path = user_directory / new_filename

        with new_file_path.open('wb+') as destination:
            for chunk in new_file.chunks():
                destination.write(chunk)

        file_type = new_file.name.split('.')[-1].lower()

        upload.path = str(new_file_path)
        upload.type = file_type
        upload.name = new_filename

        if new_page_id:
            try:
                new_page = Page.objects.get(id=new_page_id)
                upload.references_page = new_page
            except Page.DoesNotExist:
                return error_response({'error': 'Page not found'}, status.HTTP_400_BAD_REQUEST)

        upload.save()
        cache.delete(f"summarizer_output_user_{user.id}")

        serializer = UploadSerializer(upload)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FileDeleteView(APIView):
    permission_classes = [permissions.AllowAny]

    def delete(self, request, upload_id):
        token = request.headers.get('Authorization')
        if not token:
            return error_response({'error': 'Token is required in Authorization header'}, status.HTTP_401_UNAUTHORIZED)
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            if not user_id:
                return error_response({'error': 'Token is missing user ID'}, status.HTTP_401_UNAUTHORIZED)
            user = User.objects.get(id=user_id)
        except Exception as e:
            return error_response({'error': f'Invalid or expired token: {str(e)}'}, status.HTTP_401_UNAUTHORIZED)

        try:
            upload = Upload.objects.get(id=upload_id, uploaded_by=user)
        except Upload.DoesNotExist:
            return error_response({'error': 'File not found or unauthorized'}, status.HTTP_404_NOT_FOUND)

        file_path = Path(upload.path)
        if file_path.exists():
            file_path.unlink()

        upload.delete()
        cache.delete(f"summarizer_output_user_{user.id}")

        return Response({'message': 'File deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class FileRetrieveView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, upload_id):
        token = request.headers.get('Authorization')
        if not token:
            return error_response({'error': 'Token is required in Authorization header'}, status.HTTP_401_UNAUTHORIZED)
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            if not user_id:
                return error_response({'error': 'Token is missing user ID'}, status.HTTP_401_UNAUTHORIZED)
            user = User.objects.get(id=user_id)
        except Exception as e:
            return error_response({'error': f'Invalid or expired token: {str(e)}'}, status.HTTP_401_UNAUTHORIZED)

        try:
            upload = Upload.objects.get(id=upload_id, uploaded_by=user)
        except Upload.DoesNotExist:
            return error_response({'error': 'File not found or unauthorized'}, status.HTTP_404_NOT_FOUND)

        serializer = UploadSerializer(upload)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FileShowView(APIView):
    permission_classes = [permissions.AllowAny]
    CHUNK_SIZE = 1024 * 1024

    def get(self, request, upload_id):
        token = request.headers.get('Authorization')
        if not token:
            return error_response({'error': 'Token is required in Authorization header'}, status.HTTP_401_UNAUTHORIZED)
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            if not user_id:
                return error_response({'error': 'Token is missing user ID'}, status.HTTP_401_UNAUTHORIZED)
            user = User.objects.get(id=user_id)
        except Exception as e:
            return error_response({'error': f'Invalid or expired token: {str(e)}'}, status.HTTP_401_UNAUTHORIZED)

        try:
            upload = Upload.objects.get(id=upload_id, uploaded_by=user)
        except Upload.DoesNotExist:
            return error_response({'error': 'File not found or unauthorized'}, status.HTTP_404_NOT_FOUND)

        file_path = Path(upload.path)
        if not file_path.exists():
            return error_response({'error': 'File not found on server'}, status.HTTP_404_NOT_FOUND)

        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = "application/octet-stream"

        file_size = file_path.stat().st_size

        if upload.type == "csv":
            with open(file_path, "r", encoding="utf-8") as file:
                file_content = file.read(self.CHUNK_SIZE)
            response = HttpResponse(file_content, content_type="text/csv")
            response["Content-Disposition"] = f'inline; filename="{file_path.name}"'
            response["Content-Length"] = str(len(file_content))
            return response

        if file_size > self.CHUNK_SIZE:
            with open(file_path, "rb") as file:
                partial_content = file.read(self.CHUNK_SIZE)
            response = HttpResponse(partial_content, content_type=mime_type)
            response["Content-Disposition"] = f'inline; filename="{file_path.name}"'
            response["Content-Length"] = str(len(partial_content))
            response["X-File-Truncated"] = "true"
            return response

        return FileResponse(open(file_path, "rb"), content_type=mime_type)
