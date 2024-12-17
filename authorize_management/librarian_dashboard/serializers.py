from rest_framework import serializers
from common.models import Student, LibraryHistory
from django.contrib.auth.models import User
from .forms import LibraryHistoryForm 
from common.serializers import StudentDataSerializer
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.db.models import Q
from admin_dashboard.models import Librarian
from common.models import LibraryHistory # Replace `yourapp` with your actual app name
from datetime import datetime, timedelta

# Serializer for the LibraryHistory model
class LibraryHistorySerializer(serializers.ModelSerializer):
    # Use student_id directly instead of mapping to `student`

    class Meta:
        model = LibraryHistory
        fields = '__all__'
        read_only_fields = ['student']  
    def validate(self, data):
        validate_library_data(data)
        return data


def validate_library_data(data, instance=None):
    book_id = data.get('book_id')
    book_title = data.get('book_title')
    year_of_publication = data.get('year_of_publication')
    librarian_id = data.get('librarian_id')
    librarian_name = data.get('librarian_name')
    due_date = data.get('due_date')
    borrowed_date = data.get('borrowed_date')
    returned_date = data.get('returned_date')
    fines = data.get('fines')
    status = data.get('status')

    # Check if book_title and book_id combination is unique
    if book_title and book_id:
        existing_book = LibraryHistory.objects.filter(
            book_title=book_title, book_id=book_id
        ).exclude(
            history_id=instance.history_id if instance else None
        )

        if existing_book.exists():
            duplicate_status = existing_book.first().status
            if duplicate_status != "Returned":
                raise ValidationError(
                    f"A record already exists with book_title '{book_title}' and book_id '{book_id}' "
                    "and the status is not 'Returned'."
                )

    # Validate year_of_publication
    if year_of_publication:
        current_year = now().year
        try:
            if isinstance(year_of_publication, str):
                year_of_publication = int(year_of_publication)  # Convert to integer if it's a string
            if year_of_publication > current_year:
                raise ValidationError("Year of publication cannot be in the future.")
        except ValueError:
            raise ValidationError({'year_of_publication': 'Invalid year format. Use a valid year.'})

    # Validate borrowed_date and returned_date
    if returned_date:
        try:
            if isinstance(returned_date, str):
                returned_date = datetime.strptime(returned_date, '%Y-%m-%d').date()
            if isinstance(borrowed_date, str):
                borrowed_date = datetime.strptime(borrowed_date, '%Y-%m-%d').date()

            if borrowed_date and returned_date < borrowed_date:
                raise ValidationError("Returned date cannot be before borrowed date.")
            if returned_date > now().date():
                raise ValidationError("Returned date cannot be in the future.")

            data['status'] = "Returned"
        except ValueError:
            raise ValidationError({'returned_date': 'Invalid date format. Use YYYY-MM-DD.'})

    # Validate due_date
    if due_date and borrowed_date:
        try:
            if isinstance(borrowed_date, str):
                borrowed_date = datetime.strptime(borrowed_date, '%Y-%m-%d').date()
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()

            if due_date < borrowed_date:
                raise ValidationError("Due date cannot be before borrowed date.")
            if borrowed_date > now().date():
                raise ValidationError("Borrowed date cannot be in the future.")
        except ValueError:
            raise ValidationError({'due_date': 'Invalid date format. Use YYYY-MM-DD.'})

    # Calculate fines if necessary
    if returned_date and due_date:
        try:
            if isinstance(returned_date, str):
                returned_date = datetime.strptime(returned_date, '%Y-%m-%d').date()
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()

            if returned_date > due_date:
                overdue_days = (returned_date - due_date).days
                data['fines'] = overdue_days * 10  # Example fine calculation logic
        except ValueError:
            raise ValidationError({'returned_date': 'Invalid date format. Use YYYY-MM-DD.'})

    # Default status to "Borrowed" or "Overdue" based on due_date if not explicitly set
    if not data.get('status') and not returned_date:
        if due_date:
            try:
                if isinstance(due_date, str):
                    due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                if due_date < now().date():
                    data['status'] = "Overdue"
                else:
                    data['status'] = "Borrowed"
            except ValueError:
                raise ValidationError({'due_date': 'Invalid date format. Use YYYY-MM-DD.'})

