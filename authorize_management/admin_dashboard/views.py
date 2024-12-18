from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model
from datetime import datetime
from .models import User, OfficeStaff, Administrator, Librarian
from common.models import Student, FeesHistory, LibraryHistory
from .serializers import (
    UserProfileSerializer,
    AdminProfileSerializer,
    StaffProfileSerializer,
    LibrarianProfileSerializer,
    UserSerializer,  # Assuming you have a serializer for UserProfile
    validate_common_fields
)
from rest_framework.decorators import action
from .permissions import IsAdmin,IsAdminOrOfficeStaff,IsAdminOrStaffOrLibrarian,IsOfficeStaffLibrary
# Common required fields
COMMON_REQUIRED_FIELDS = ['date_of_birth', 'gender', 'address', 'phone_number','date_of_joining','employee_id']

# Role-specific required fields
ROLE_REQUIRED_FIELDS = {
    'admin': COMMON_REQUIRED_FIELDS + [ 'designation'],
    'staff': COMMON_REQUIRED_FIELDS + [ 'position', 'department'],
    'librarian': COMMON_REQUIRED_FIELDS + [ 'assigned_section'],
}

def validate_required_fields(profile_data, required_fields):
    """Validate that all required fields are present in the profile data."""
    missing_fields = [field for field in required_fields if not profile_data.get(field)]
    return missing_fields

def create_profile(role, user, profile_data):
    """Create a profile for the given role."""
    if role == 'staff':
        return OfficeStaff.objects.create(user=user, **profile_data), StaffProfileSerializer
    elif role == 'admin':
        return Administrator.objects.create(user=user, **profile_data), AdminProfileSerializer
    elif role == 'librarian':
        return Librarian.objects.create(user=user, **profile_data), LibrarianProfileSerializer
    else:
        return None, None

  
User = get_user_model()

class UserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    def get_permissions(self):
        if self.action == 'create_user':
            return [IsAdmin()]  # Admin-only action
        elif self.action in ['update_user', 'partial_update_user']:
            return [IsAdminOrStaffOrLibrarian()]  # For admin or staff
        elif self.action == 'delete_user':
            return [IsAdmin()]  # Admin-only action
        elif self.action == 'retrieve_user':
            return [IsAdminOrStaffOrLibrarian()]
        elif self.action == 'retrieve_all_users':
            return [IsAdmin()]
        return super().get_permissions()
    @action(detail=False, methods=['post'], url_path='create-user')
    def create_user(self, request):
        required_fields = ['is_active', 'is_staff']
        for field in required_fields:
            if field not in request.data:
                return Response({field: f'{field} is required to create a user.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            password = request.data.get('password')
            if not password:
                return Response({'message': 'Password field is required.'}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            user.set_password(password)
            user.save()

            return Response({'message': 'User created successfully.', 'user': serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response({'message': 'Invalid data.', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='retrieve-user')
    def retrieve_user(self, request, pk=None):
        try:
            user = User.objects.get(id=pk)
            serializer = UserSerializer(user)
            return Response({'message': 'User retrieved successfully.', 'user': serializer.data}, status=200)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=404)

    @action(detail=False, methods=['get'], url_path='retrieve-users')
    def retrieve_all_users(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({'message': 'Users retrieved successfully.', 'users': serializer.data}, status=200)

    @action(detail=True, methods=['put'], url_path='update-user')
    def update_user(self, request, pk=None):
        try:
            user = User.objects.get(id=pk)

            # Admin can update any user's profile, including their status
            if request.user.has_perm('admin'):  # Use IsAdmin permission
                return self._handle_user_update(user, request.data)

            # Regular users can only update their own profile
            if request.user.id == user.id:
                return self._handle_user_update(user, request.data)

            return Response({'message': 'You do not have permission to update this user.'}, status=403)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=404)

    def _handle_user_update(self, user, data):
        if 'password' in data:
            user.set_password(data.pop('password'))

        if 'status' in data and not user.has_perm('admin'):
            return Response({'message': 'Only admins can update the status of other users.'}, status=403)

        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User updated successfully.', 'user': serializer.data}, status=200)

        return Response({'message': 'Invalid data.', 'errors': serializer.errors}, status=400)

    @action(detail=True, methods=['delete'], url_path='delete-user')
    def delete_user(self, request, pk=None):
        if not request.user.has_perm('admin'):  # Check for admin permission
            return Response({'message': 'You do not have permission to delete users.'}, status=status.HTTP_403_FORBIDDEN)       
        confirm = request.query_params.get('confirm', 'false')
        
        if confirm != 'true':
            return Response(
                {
                    'message': f'Are you sure you want to delete the user with ID {pk}? Please confirm by setting ?confirm=true in your request.'
                },
                status=status.HTTP_200_OK
            )     
        try:
            user = User.objects.get(id=pk)
            user.delete()
            return Response({'message': 'User deleted successfully.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    def _handle_user_update(self, user, data):
        if 'password' in data:
            user.set_password(data.pop('password'))
        if 'status' in data and user.role != 'admin':
            return Response({'message': 'Only admins can update the status of other users.'}, status=403)
        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User updated successfully.', 'user': serializer.data}, status=200)
        return Response({'message': 'Invalid data.', 'errors': serializer.errors}, status=400)

    @action(detail=True, methods=['delete'], url_path='delete-user')
    def delete_user(self, request, pk=None):
        if request.user.role != 'admin':
            return Response({'message': 'You do not have permission to delete users.'}, status=status.HTTP_403_FORBIDDEN)        
        confirm = request.query_params.get('confirm', 'false')     
        if confirm != 'true':
            return Response(
                {
                    'message': f'Are you sure you want to delete the user with ID {pk}? Please confirm by setting ?confirm=true in your request.'
                },
                status=status.HTTP_200_OK
            )       
        try:
            user = User.objects.get(id=pk)
            user.delete()
            return Response({'message': 'User deleted successfully.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure that only authenticated users can access the profile
    def get(self, request):
        user = request.user  
        try:
            user_serializer = UserProfileSerializer(user)
            user_data = user_serializer.data
        except Exception as e:
            return Response({'message': 'User info could not be retrieved', 'error': str(e)}, status=500)    
        # Check if the user's role is valid
        if user.role:
            # If the role exists, fetch role-specific information
            if user.role == 'admin':
                try:
                    admin_profile = Administrator.objects.get(user=user)
                    admin_serializer = AdminProfileSerializer(admin_profile)
                    user_data['profile'] = admin_serializer.data  # Add the admin profile data
                    return Response(user_data)
                except Administrator.DoesNotExist:
                    return Response({'message': 'Admin profile not found'}, status=404)
            elif user.role == 'staff':
                try:
                    staff_profile = OfficeStaff.objects.get(user=user)
                    staff_serializer = StaffProfileSerializer(staff_profile)
                    user_data['profile'] = staff_serializer.data  # Add the staff profile data
                    return Response(user_data)

                except OfficeStaff.DoesNotExist:
                    return Response({'message': 'Staff profile not found'}, status=404)
            elif user.role == 'librarian':
                try:
                    librarian_profile = Librarian.objects.get(user=user)
                    librarian_serializer = LibrarianProfileSerializer(librarian_profile)
                    user_data['profile'] = librarian_serializer.data  # Add the librarian profile data
                    return Response(user_data)
                except Librarian.DoesNotExist:
                    return Response({'message': 'Librarian profile not found'}, status=404)

            return Response({'message': 'Invalid role'}, status=400)

        # If no role is found, return only the user info
        return Response(user_data)

class UpdateUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        user = request.user
        # Only allow updates if the user is an admin or the profile belongs to the current user
        if user.role != 'admin' and user.id != id:
            return Response({'message': 'You do not have permission to update this user information.'}, status=403)
        try:
            # Fetch the user to update
            user_to_update = User.objects.get(id=id)
            data = request.data
            print("Received Data:", data)  # Debug input data
            # Update role-specific profile
            if user_to_update.role == 'admin':
                try:
                    profile = Administrator.objects.get(user=user_to_update)
                except Administrator.DoesNotExist:
                    return Response({'message': 'Administrator profile not found.'}, status=404)

                profile_data = data  # Admin profile data is passed as 'admin_profile' in request data
                # Validate the profile data
                try:
                    validate_common_fields(profile_data)  # Reuse the common validation
                except ValidationError as e:
                    return Response({'message': str(e)}, status=400)
                # Perform the update using the serializer
                serializer = AdminProfileSerializer(profile, data=profile_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated_profile = Administrator.objects.get(user=user_to_update)
                    return Response({'message': 'User updated successfully.', 'profile': serializer.data}, status=200)
                else:
                    return Response(serializer.errors, status=400)
            elif user_to_update.role == 'staff':
                try:
                    profile = OfficeStaff.objects.get(user=user_to_update)
                except OfficeStaff.DoesNotExist:
                    return Response({'message': 'Office Staff profile not found.'}, status=404)
                profile_data = data  # Office Staff profile data passed similarly
                try:
                    validate_common_fields(profile_data)  # Reuse the common validation
                except ValidationError as e:
                    return Response({'message': str(e)}, status=400)
                # Perform the update using the serializer
                serializer = StaffProfileSerializer(profile, data=profile_data, partial=True)

                if serializer.is_valid():
                    serializer.save()
                    updated_profile = OfficeStaff.objects.get(user=user_to_update)

                    return Response({'message': 'User updated successfully.', 'profile': serializer.data}, status=200)
                else:
                    return Response(serializer.errors, status=400)

            elif user_to_update.role == 'librarian':
                try:
                    profile = Librarian.objects.get(user=user_to_update)
                except Librarian.DoesNotExist:
                    return Response({'message': 'Librarian profile not found.'}, status=404)

                profile_data = data  # Librarian profile data passed similarly
                try:
                    validate_common_fields(profile_data)  # Reuse the common validation
                except ValidationError as e:
                    return Response({'message': str(e)}, status=400)
                serializer = LibrarianProfileSerializer(profile, data=profile_data, partial=True)

                if serializer.is_valid():
                    serializer.save()
                    updated_profile = Librarian.objects.get(user=user_to_update)

                    return Response({'message': 'User updated successfully.', 'profile': serializer.data}, status=200)
                else:
                    return Response(serializer.errors, status=400)

            else:
                return Response({'message': 'Invalid role.'}, status=400)

        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=404)
        except (Administrator.DoesNotExist, OfficeStaff.DoesNotExist, Librarian.DoesNotExist):
            return Response({'message': 'Role-specific profile not found.'}, status=404)


# User = get_user_model()  # Get the custom User model

class CreateRoleProfileView(APIView):
    permission_classes = [IsAuthenticated,IsAdmin]

    def post(self, request, user_id, role):
        try:
            user = User.objects.get(id=user_id)  # Using custom User model
        except User.DoesNotExist:
            return Response({'message': 'User does not exist.'}, status=404)

        if user.role != role:  # Check if the user's role matches the requested role
            return Response({'message': 'User role mismatch.'}, status=400)
        profile_data = request.data
        try:
            validate_common_fields(profile_data)
        except ValidationError as e:
            return Response({'message': 'Validation error', 'errors': e.message_dict}, status=400)
        required_fields = ROLE_REQUIRED_FIELDS.get(role, [])
        missing_fields = validate_required_fields(profile_data, required_fields)
        if missing_fields:
            return Response({'message': f'Missing required fields: {", ".join(missing_fields)}'}, status=400)
        try:
            profile, serializer_class = create_profile(role, user, profile_data)
            if not profile:
                return Response({'message': 'Invalid role provided.'}, status=400)
            serializer = serializer_class(profile)
            return Response({'message': 'Profile created successfully.', 'profile': serializer.data}, status=201)
        except Exception as e:
            return Response({'message': f'Error creating profile: {str(e)}'}, status=500)

class RetrieveRoleProfileView(APIView):
    permission_classes = [IsAuthenticated,IsAdmin]
    def get(self, request, id):
        user = request.user
        try:
            user_to_retrieve = User.objects.get(id=id)
            user_data = UserProfileSerializer(user_to_retrieve).data
            if user_to_retrieve.role == 'admin':
                try:
                    profile = Administrator.objects.get(user=user_to_retrieve)
                    profile_data = AdminProfileSerializer(profile).data
                except Administrator.DoesNotExist:
                    profile_data = {}
            elif user_to_retrieve.role == 'staff':
                try:
                    profile = OfficeStaff.objects.get(user=user_to_retrieve)
                    profile_data = StaffProfileSerializer(profile).data
                except OfficeStaff.DoesNotExist:
                    profile_data = {}
            elif user_to_retrieve.role == 'librarian':
                try:
                    profile = Librarian.objects.get(user=user_to_retrieve)
                    profile_data = LibrarianProfileSerializer(profile).data
                except Librarian.DoesNotExist:
                    profile_data = {}
            else:
                profile_data = {}
            return Response({'user': user_data, 'profile': profile_data}, status=200)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=404)

class RetrieveProfilesView(APIView):
    permission_classes = [IsAuthenticated,IsAdmin]

    def get(self, request, role):
        user = request.user
        users = User.objects.filter(role=role)
        if not users.exists():
            return Response({'message': f'No users found for role: {role}'}, status=404)
        user_profiles = []
        for user in users:
            user_data = UserProfileSerializer(user).data
            profile_data = {}
            try:
                if role == 'admin':
                    profile = Administrator.objects.get(user=user)
                    profile_data = AdminProfileSerializer(profile).data
                elif role == 'staff':
                    profile = OfficeStaff.objects.get(user=user)
                    profile_data = StaffProfileSerializer(profile).data
                elif role == 'librarian':
                    profile = Librarian.objects.get(user=user)
                    profile_data = LibrarianProfileSerializer(profile).data
            except (Administrator.DoesNotExist, OfficeStaff.DoesNotExist, Librarian.DoesNotExist):
                # Handle the case where the profile doesn't exist
                profile_data = {'message': f'{role.capitalize()} profile not found.'}
            user_profiles.append({'user': user_data, 'profile': profile_data})
        return Response({'users_profiles': user_profiles}, status=200)


class DeleteProfileView(APIView):
    permission_classes = [IsAuthenticated,IsAdmin]
    def delete(self, request, id):
        user = request.user
        # Check for confirmation query parameter
        confirm = request.query_params.get('confirm', 'false')    
        if confirm != 'true':
            # Return a message asking for confirmation
            return Response(
                {
                    'message': f'Are you sure you want to delete the profile of the user with ID {id}? Please confirm by setting ?confirm=true in your request.'
                },
                status=200
            )
        try:
            user_to_delete_profile = User.objects.get(id=id)
            if user_to_delete_profile.role == 'admin':
                Administrator.objects.filter(user=user_to_delete_profile).delete()  # Use filter instead of get
            elif user_to_delete_profile.role == 'staff':
                OfficeStaff.objects.filter(user=user_to_delete_profile).delete()  # Use filter instead of get
            elif user_to_delete_profile.role == 'librarian':
                Librarian.objects.filter(user=user_to_delete_profile).delete()  # Use filter instead of get
            else:
                return Response({'message': 'No profile found for the user.'}, status=404)
            return Response({'message': 'User profile deleted successfully.'}, status=200)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=404)
        except Exception as e:
            return Response({'message': f'Error occurred: {str(e)}'}, status=500)