from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import LibraryHistorySerializer 
from django.shortcuts import get_object_or_404
from .forms import LibraryHistoryForm
from common.models import LibraryHistory,Student
from rest_framework import viewsets
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from .serializers import validate_library_data
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from rest_framework.exceptions import ValidationError as DRFValidationError
# Assuming you have the following permissions
from admin_dashboard.permissions import IsAdmin,  IsLibrarian, IsAdminOrStaffOrLibrarian,IsOfficeStaffLibrary,IsOfficeStaff
class LibraryHistoryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    def get_permissions(self):
        """
        Override the `get_permissions` method to apply different permissions for different actions.
        """
        if self.action == 'list':
            # For listing library histories, allow access to admins, librarians, and staff
            permission_classes = [IsAdminOrStaffOrLibrarian]
        elif self.action in ['retrieve_by_student', 'retrieve_by_history_and_student']:
            # For retrieving specific student history or history records by student
            permission_classes = [IsAdminOrStaffOrLibrarian]
        elif self.action in ['create','update','destroy']:
            permission_classes = [IsAdmin]
        elif self.action in ['update_status','view_history']:
            permission_classes=[IsAdminOrStaffOrLibrarian]
        else:
            permission_classes = []

        return [permission() for permission in permission_classes]
    def _check_role(self, user, roles):
        return user.role in roles

    def list(self, request):
       
        library_histories = LibraryHistory.objects.all()
        serializer = LibraryHistorySerializer(library_histories, many=True)
        return Response(serializer.data)
        
    def retrieve_by_student(self, request, student_id=None):
        # Get the student by student_id
        student = get_object_or_404(Student, student_id=student_id)

        # Get all library history records for that student
        library_histories = LibraryHistory.objects.filter(student=student)
        serializer = LibraryHistorySerializer(library_histories, many=True)
        return Response(serializer.data)

    def retrieve_by_history_and_student(self, request, student_id=None, history_id=None):

        # Get the student by student_id
        student = get_object_or_404(Student, student_id=student_id)

        # Get the specific library history record by history_id
        library_history = get_object_or_404(LibraryHistory, pk=history_id, student=student)

        serializer = LibraryHistorySerializer(library_history)
        return Response(serializer.data)

  
    def create(self, request, student_id=None, *args, **kwargs):
        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            return Response({"message": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
        
        book_id = request.data.get('book_id')
        borrowed_date = request.data.get('borrowed_date')

        try:
            validate_library_data(request.data)
        except ValidationError as e:
            error_details = {
                "message": "Validation error occurred.",
                "errors": e.message_dict if hasattr(e, "message_dict") else str(e)
            }
            return Response(error_details, status=status.HTTP_400_BAD_REQUEST)
        
        existing_history = LibraryHistory.objects.filter(student=student, book_id=book_id, borrowed_date=borrowed_date).exists()
        if existing_history:
            return Response({"message": "Duplicate data: The same book has already been borrowed on this date."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LibraryHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=student)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "Serialization error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, student_id=None, pk=None):
        student = get_object_or_404(Student, student_id=student_id)
        library_history = get_object_or_404(LibraryHistory, pk=pk, student=student)
        
        confirm = request.query_params.get('confirm', 'false')
        
        if confirm != 'true':
            return Response(
                {
                    'message': f'Are you sure you want to delete the library history record for {library_history.book_title}? Please confirm by setting ?confirm=true in your request.'
                },
                status=status.HTTP_200_OK
            )
        
        library_history.delete()
        return Response({'message': 'Library history record deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

    def update(self, request, student_id=None, pk=None):
        if not self._check_role(request.user, ['admin']):
            return Response({'message': 'You do not have permission to edit this library history record.'},
                            status=status.HTTP_403_FORBIDDEN)
        
        student = get_object_or_404(Student, student_id=student_id)
        library_history = get_object_or_404(LibraryHistory, pk=pk, student=student)
        
        try:
            validate_library_data(request.data)
        except ValidationError as e:
            error_details = {
                "message": "Validation error occurred.",
                "errors": e.message_dict if hasattr(e, "message_dict") else str(e)
            }
            return Response(error_details, status=status.HTTP_400_BAD_REQUEST)

        serializer = LibraryHistorySerializer(library_history, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, student_id=None, pk=None):
        if request.user.role == 'librarian':
            librarian_name = request.data.get('first_name')
            librarian_id = request.data.get('id')
        
            if not librarian_name and not librarian_id:
                return Response({'message': 'Librarian name and ID must be provided when updating status.'},
                                status=status.HTTP_400_BAD_REQUEST)
            
        student = get_object_or_404(Student, student_id=student_id)
        library_history = get_object_or_404(LibraryHistory, pk=pk, student=student)

        if library_history.status == 'Returned':
            return Response({'message': 'This record has already been returned and cannot be updated.'},
                            status=status.HTTP_403_FORBIDDEN)

        form = LibraryHistoryForm(request.data, instance=library_history, partial=True)

        try:
            validate_library_data(request.data)
        except ValidationError as e:
            error_details = {
                "message": "Validation error occurred.",
                "errors": e.message_dict if hasattr(e, "message_dict") else str(e)
            }
            return Response(error_details, status=status.HTTP_400_BAD_REQUEST)

        if form.is_valid():
            form.save()
            updated_library_history = LibraryHistorySerializer(library_history)
            return Response({
                'message': 'Status updated successfully.',
                'data': updated_library_history.data
            }, status=status.HTTP_200_OK)

        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def view_history(self, request):
        library_histories = LibraryHistory.objects.all()
        serializer = LibraryHistorySerializer(library_histories, many=True)
        return Response(serializer.data)