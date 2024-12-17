from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_bytes, smart_str
from common.serializers import StudentSerializer
from common.models import Student
from .serializers import (
    LoginSerializer,
    SetNewPasswordSerializer,
    PasswordForgotSerializer,
    validate_student_data
)
from admin_dashboard.permissions import IsAdmin, IsAdminOrOfficeStaff, IsLibrarian, IsOfficeStaff
from admin_dashboard.models import User
from rest_framework.permissions import IsAuthenticated


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data['username']
            role = serializer.validated_data['role']
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                user = User.objects.filter(username=username, role=role, email=email).first()
                
                if user is None:
                    return Response({'message': 'User not found with the given credentials (username, role, email).'}, status=400)
                
                if not user.check_password(password):
                    return Response({'message': 'Incorrect password provided.'}, status=400)

                refresh = RefreshToken.for_user(user)
                return Response({
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                })

            except Exception as e:
                return Response({'message': f'Error occurred during authentication: {str(e)}'}, status=500)
        
        return Response({'message': 'Invalid data provided in the request.'}, status=400)

# Set new password view
class SetNewPasswordView(generics.UpdateAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user  # Get the authenticated user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set the new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'detail': 'Password has been updated successfully.'}, status=status.HTTP_200_OK)


# Forgot password view
class PasswordForgotView(generics.GenericAPIView):
    serializer_class = PasswordForgotSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Validate the input (email only)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            # Find the user by email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'details': 'User with the given email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate the password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(smart_bytes(user.pk))

        # Generate the reset link
        reset_link = f"http://127.0.0.1:8000/api/common/password-reset/{uid}/{token}/"

        # Send the reset email
        send_mail(
            'Password Reset Request',
            f"Use the following link to reset your password: {reset_link}",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        return Response({'details': 'Password reset link has been sent to your email.'}, status=status.HTTP_200_OK)


# Reset password view
class ResetPasswordView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            # Decode the UID and retrieve the user
            uid = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # Verify the token and reset the password
        if user is not None and default_token_generator.check_token(user, token):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'details': 'Password has been reset successfully'}, status=status.HTTP_200_OK)

        return Response({'details': 'Invalid token or User ID'}, status=status.HTTP_400_BAD_REQUEST)




# Student ViewSet
class StudentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated, IsAdmin |  IsOfficeStaff | IsLibrarian]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdmin | IsOfficeStaff]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        student = self.get_object()
        serializer = StudentSerializer(student, data=request.data, partial=True)
        updated_data = student.__dict__.copy()
        updated_data.update(request.data)

        fields_to_update = {key: value for key, value in updated_data.items() if key not in ['_state', 'id']}
        try:
            validate_student_data(fields_to_update)
        except ValidationError as e:
            return Response({'message': str(e)}, status=400)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Student updated successfully.', 'student': serializer.data}, status=status.HTTP_200_OK)

        return Response({'message': 'Invalid data.', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        required_fields = ['full_name', 'date_of_birth', 'gender', 'address', 'student_class', 'roll_number', 'guardian_phone_number', 'guardian_name', 'email', 'admission_number', 'admission_date']
        profile_data=request.data
        try:
            # Perform validation using your custom validation function
            validate_student_data(profile_data)
        except ValidationError as e:
            # Return a custom error response if validation fails
            return Response({'message': 'Validation error', 'errors': e.message_dict}, status=400)

        
        # Check if any required fields are missing
        missing_fields = [field for field in required_fields if field not in profile_data or not profile_data[field]]
        if missing_fields:
            return Response({'message': 'Missing required fields.', 'missing_fields': missing_fields}, status=400)
        
        # Call the super class's create method if validation passes
        return super().create(request, *args, **kwargs)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get(self, request):
        try:
            students = Student.objects.filter(is_deleted=False)
            if not students.exists():
                return Response({'message': 'No students found.'}, status=status.HTTP_404_NOT_FOUND)

            serializer = StudentSerializer(students, many=True)
            return Response({'message': 'Students retrieved successfully.', 'students': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
    def destroy(self, request, *args, **kwargs):
        # Check for the 'confirm' query parameter
        confirm = request.query_params.get('confirm', None)
        if confirm != 'true':
            raise ValidationError("Please confirm the deletion by adding '?confirm=true' to the request.")

        try:
            student = self.get_object()  # Retrieves the student object using self.get_object()
            student.delete()  # Deletes the student record
            return Response({'message': 'Student deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except Student.DoesNotExist:
            return Response({'message': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)