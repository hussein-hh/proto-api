import re  # used for working with text patterns
import jwt  # used to decode and verify tokens
from pathlib import Path  # handles file and directory operations
from datetime import datetime  # helps with getting the current time
from django.conf import settings  # gets settings from the django project
from django.contrib.auth.models import User  # imports the user model
from rest_framework import status, permissions, parsers  # imports tools for handling api requests
from rest_framework.views import APIView  # base class for making api views
from rest_framework.response import Response  # makes api responses easier to manage
from .serializers import UploadSerializer  # imports a serializer to format the uploaded file data
from .models import Upload  # imports the upload model to save file info in the database
from Domains.Onboard.models import Business  # imports the business model to link users with businesses
from django.http import HttpResponse, FileResponse
import mimetypes


def slugify(text):
    """simple function to convert text into a safe format for folder names"""
    return re.sub(r'[\W_]+', '_', text).strip('_').lower()  # replaces special characters with underscores, removes extra underscores, and makes text lowercase  


def error_response(message, status_code):
    """Helper function to create response objects for better readability"""
    return Response(message, status=status_code)


class FileUploadView(APIView):  # defines an api endpoint for file uploads
    permission_classes = [permissions.AllowAny]  # allows anyone to use this endpoint
    parser_classes = [parsers.MultiPartParser]  # allows handling of file uploads

    def post(self, request):  # handles post requests when a file is uploaded
        token = request.data.get('token')  # gets the token from the request

        if not token:  # checks if the token is missing
            return error_response({'error': 'Token is required'}, status.HTTP_401_UNAUTHORIZED)  # sends an error response

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])  # decodes the token using the secret key
            user_id = decoded_token.get('user_id')  # extracts the user id from the token

            if not user_id:  # checks if the user id is missing
                return error_response({'error': 'Token is missing user ID'}, status.HTTP_401_UNAUTHORIZED)  # sends an error response

            user = User.objects.get(id=user_id)  # fetches the user from the database using the id
        except Exception as e:  # if something goes wrong with decoding the token
            return error_response({'error': f'Invalid or expired token: {str(e)}'}, status.HTTP_401_UNAUTHORIZED)  # sends an error response

        uploaded_file = request.FILES.get('file')  # gets the uploaded file from the request
        file_name = request.data.get('name')  # gets the file name from the request

        if not uploaded_file or not file_name:  # checks if the file or file name is missing
            return error_response({'error': 'File and name are required'}, status.HTTP_400_BAD_REQUEST)  # sends an error response

        try:
            business = Business.objects.get(user=user)  # tries to get the business linked to the user
        except Business.DoesNotExist:  # if no business is found for the user
            return error_response({'error': 'Business not found for user'}, status.HTTP_404_NOT_FOUND)  # sends an error response

        business_type_slug = slugify(business.category)  # converts the business category into a safe format
        business_name = business.name
        business_id = business.id  # gets the business id
        user_name = user.username
        user_id_str = str(user.id)  # converts the user id to a string

        user_directory = Path("uploads") / business_type_slug / str(business_id) / user_id_str  # creates a folder path for the user's files
        user_directory.mkdir(parents=True, exist_ok=True)  # makes sure the folder exists (creates it if needed)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # gets the current date and time in a safe format
        new_filename = f"{timestamp}_{business_name}_{business_id}_{user_name}_{user_id_str}_{file_name}"  # creates a unique file name using the timestamp and user info

        file_path = user_directory / new_filename  # creates the full file path

        with file_path.open('wb+') as destination:  # opens the file to write data
            for chunk in uploaded_file.chunks():  # reads the file in small parts (chunks)
                destination.write(chunk)  # writes each chunk to the file

        file_type = uploaded_file.name.split('.')[-1].lower()  # gets the file extension (like jpg, pdf, etc.) and makes it lowercase

        uploaded_file_record = Upload.objects.create(  # saves the file info in the database
            path=str(file_path),  # stores the file location
            type=file_type,  # stores the file type
            uploaded_by=user,  # stores the user who uploaded it
            name=new_filename  # stores the new unique file name
        )

        serializer = UploadSerializer(uploaded_file_record)  # formats the uploaded file data
        return error_response(serializer.data, status.HTTP_201_CREATED)  # returns the uploaded file info as a response


class FileListView(APIView):  # defines an api endpoint for listing user files
    permission_classes = [permissions.AllowAny]  # allows anyone to access this endpoint

    def get(self, request):  # handles GET requests to retrieve a list of uploaded files
        token = request.headers.get('Authorization')  # gets the token from the Authorization header

        if not token:  # checks if the token is missing
            return error_response({'error': 'Token is required in Authorization header'}, status.HTTP_401_UNAUTHORIZED)  # sends an error response

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])  # decodes the token using the secret key
            user_id = decoded_token.get('user_id')  # extracts the user id from the token

            if not user_id:  # checks if the user id is missing in the token
                return error_response({'error': 'Token is missing user ID'}, status.HTTP_401_UNAUTHORIZED)  # sends an error response

            user = User.objects.get(id=user_id)  # fetches the user from the database using the id
        except Exception as e:  # if an error occurs during token decoding or user retrieval
            return error_response({'error': f'Invalid or expired token: {str(e)}'}, status.HTTP_401_UNAUTHORIZED)  # sends an error response

        uploads = Upload.objects.filter(uploaded_by=user)  # retrieves all uploads linked to the user
        serializer = UploadSerializer(uploads, many=True)  # formats the uploaded file data
        return Response(serializer.data, status=status.HTTP_200_OK)  # returns the list of files as a response


class FileUpdateView(APIView):  # defines an api endpoint for updating an uploaded file
    permission_classes = [permissions.AllowAny]  # allows anyone to access this endpoint
    parser_classes = [parsers.MultiPartParser]  # allows handling of file uploads

    def put(self, request, upload_id):  # handles PUT requests to update a file
        token = request.headers.get('Authorization')  # gets the token from the Authorization header

        if not token:  # checks if the token is missing
            return error_response({'error': 'Token is required in Authorization header'}, status.HTTP_401_UNAUTHORIZED)  # sends an error response

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])  # decodes the token using the secret key
            user_id = decoded_token.get('user_id')  # extracts the user id from the token

            if not user_id:  # checks if the user id is missing in the token
                return error_response({'error': 'Token is missing user ID'}, status.HTTP_401_UNAUTHORIZED)  # sends an error response

            user = User.objects.get(id=user_id)  # fetches the user from the database using the id
        except Exception as e:  # if an error occurs during token decoding or user retrieval
            return error_response({'error': f'Invalid or expired token: {str(e)}'}, status.HTTP_401_UNAUTHORIZED)  # sends an error response

        try:
            upload = Upload.objects.get(id=upload_id, uploaded_by=user)  # retrieves the upload record ensuring it belongs to the user
        except Upload.DoesNotExist:  # if the file does not exist or the user is unauthorized
            return error_response({'error': 'File not found or unauthorized'}, status.HTTP_404_NOT_FOUND)  # sends an error response

        new_file = request.FILES.get('file')  # gets the new file from the request
        new_name = request.data.get('name')  # gets the new name for the file from the request

        if not new_file or not new_name:  # checks if the new file or new name is missing
            return error_response({'error': 'New file and name are required'}, status.HTTP_400_BAD_REQUEST)  # sends an error response

        old_file_path = Path(upload.path)  # gets the path of the old file
        if old_file_path.exists():  # checks if the old file exists
            old_file_path.unlink()  # removes the old file from storage

        try:
            business = Business.objects.get(user=user)  # tries to get the business linked to the user
        except Business.DoesNotExist:  # if no business is found for the user
            return error_response({'error': 'Business not found for user'}, status.HTTP_404_NOT_FOUND)  # sends an error response

        business_type_slug = slugify(business.category)  # converts the business category into a safe format
        business_name = business.name
        business_id = business.id  # gets the business id
        user_id_str = str(user.id)  # converts the user id to a string

        user_directory = Path("uploads") / business_type_slug / str(business_id) / user_id_str  # creates a folder path for the user's files
        user_directory.mkdir(parents=True, exist_ok=True)  # makes sure the folder exists (creates it if needed)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # gets the current date and time in a safe format
        new_filename = f"{timestamp}_{business_name}_{business_id}_{user.username}_{user_id_str}_{new_name}"  # creates a unique file name using the timestamp and user info

        new_file_path = user_directory / new_filename  # creates the full file path for the new file

        with new_file_path.open('wb+') as destination:  # opens the file to write data
            for chunk in new_file.chunks():  # reads the new file in small parts (chunks)
                destination.write(chunk)  # writes each chunk to the new file

        file_type = new_file.name.split('.')[-1].lower()  # gets the file extension and makes it lowercase

        upload.path = str(new_file_path)  # updates the file path in the upload record
        upload.type = file_type  # updates the file type in the upload record
        upload.name = new_filename  # updates the file name in the upload record
        upload.save()  # saves the updated upload record in the database

        serializer = UploadSerializer(upload)  # formats the updated file data
        return Response(serializer.data, status=status.HTTP_200_OK)  # returns the updated file info as a response


class FileDeleteView(APIView):  # defines an api endpoint for deleting an uploaded file
    permission_classes = [permissions.AllowAny]  # allows anyone to access this endpoint

    def delete(self, request, upload_id):  # handles DELETE requests to remove a file
        token = request.headers.get('Authorization')  # gets the token from the Authorization header

        if not token:  # checks if the token is missing
            return error_response({'error': 'Token is required in Authorization header'}, status.HTTP_401_UNAUTHORIZED)  # sends an error response

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])  # decodes the token using the secret key
            user_id = decoded_token.get('user_id')  # extracts the user id from the token

            if not user_id:  # checks if the user id is missing in the token
                return error_response({'error': 'Token is missing user ID'}, status.HTTP_401_UNAUTHORIZED)  # sends an error response

            user = User.objects.get(id=user_id)  # fetches the user from the database using the id
        except Exception as e:  # if an error occurs during token decoding or user retrieval
            return error_response({'error': f'Invalid or expired token: {str(e)}'}, status.HTTP_401_UNAUTHORIZED)  # sends an error response

        try:
            upload = Upload.objects.get(id=upload_id, uploaded_by=user)  # retrieves the upload record ensuring it belongs to the user
        except Upload.DoesNotExist:  # if the file does not exist or the user is unauthorized
            return error_response({'error': 'File not found or unauthorized'}, status.HTTP_404_NOT_FOUND)  # sends an error response

        file_path = Path(upload.path)  # gets the path of the file to be deleted
        if file_path.exists():  # checks if the file exists
            file_path.unlink()  # removes the file from storage

        upload.delete()  # deletes the upload record from the database

        return Response({'message': 'File deleted successfully'}, status=status.HTTP_204_NO_CONTENT)  # returns a success message


class FileRetrieveView(APIView):  # defines an api endpoint for retrieving details of an uploaded file
    permission_classes = [permissions.AllowAny]  # allows anyone to access this endpoint

    def get(self, request, upload_id):  # handles GET requests to retrieve file details
        token = request.headers.get('Authorization')  # gets the token from the Authorization header

        if not token:  # checks if the token is missing
            return error_response({'error': 'Token is required in Authorization header'}, status.HTTP_401_UNAUTHORIZED)  # sends an error response

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])  # decodes the token using the secret key
            user_id = decoded_token.get('user_id')  # extracts the user id from the token

            if not user_id:  # checks if the user id is missing in the token
                return error_response({'error': 'Token is missing user ID'}, status.HTTP_401_UNAUTHORIZED)  # sends an error response

            user = User.objects.get(id=user_id)  # fetches the user from the database using the id
        except Exception as e:  # if an error occurs during token decoding or user retrieval
            return error_response({'error': f'Invalid or expired token: {str(e)}'}, status.HTTP_401_UNAUTHORIZED)  # sends an error response

        try:
            upload = Upload.objects.get(id=upload_id, uploaded_by=user)  # retrieves the upload record ensuring it belongs to the user
        except Upload.DoesNotExist:  # if the file does not exist or the user is unauthorized
            return error_response({'error': 'File not found or unauthorized'}, status.HTTP_404_NOT_FOUND)  # sends an error response

        serializer = UploadSerializer(upload)  # formats the file data
        return Response(serializer.data, status=status.HTTP_200_OK)  # returns the file details as a response
        
class FileShowView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, upload_id):
        token = request.headers.get('Authorization')  # gets the token from the Authorization header

        if not token:  # checks if the token is missing
            return error_response({'error': 'Token is required in Authorization header'}, status.HTTP_401_UNAUTHORIZED)  # sends an error response

        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])  # decodes the token using the secret key
            user_id = decoded_token.get('user_id')  # extracts the user id from the token

            if not user_id:  # checks if the user id is missing in the token
                return error_response({'error': 'Token is missing user ID'}, status.HTTP_401_UNAUTHORIZED)  # sends an error response

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

        if upload.type == "csv":
            response = HttpResponse(file_path.open("r"), content_type="text/csv")
            response["Content-Disposition"] = f'inline; filename="{file_path.name}"'
            return response

        return FileResponse(open(file_path, "rb"), content_type=mime_type)
