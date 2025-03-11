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
