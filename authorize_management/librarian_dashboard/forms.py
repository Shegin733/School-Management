# forms.py
from django import forms
from common.models import LibraryHistory
from django.utils import timezone
from django.core.exceptions import ValidationError

class LibraryHistoryForm(forms.ModelForm):
    class Meta:
        model = LibraryHistory
        fields = [
            'book_id', 'book_title', 'author', 'publisher', 'isbn',
            'genre', 'edition', 'year_of_publication', 'language',
            'borrowed_date', 'due_date', 'returned_date', 'status', 
            'fines', 'condition', 'remarks', 'reservation_details', 'renewal_history'
        ]

    def __init__(self, *args, **kwargs):
        partial = kwargs.pop('partial', False)  # Extract partial argument
        super().__init__(*args, **kwargs)

        if partial:
            # If partial=True, set fields to not be required
            for field in self.fields.values():
                field.required = False

        # Disable the fields if the book is returned
        if self.instance and self.instance.returned_date:
            self.fields['book_id'].disabled = True
            self.fields['book_title'].disabled = True
            self.fields['author'].disabled = True
            self.fields['publisher'].disabled = True
            self.fields['isbn'].disabled = True
            self.fields['genre'].disabled = True
            self.fields['edition'].disabled = True
            self.fields['year_of_publication'].disabled = True
            self.fields['language'].disabled = True
            self.fields['borrowed_date'].disabled = True
            self.fields['due_date'].disabled = True
            self.fields['status'].disabled = True
            self.fields['fines'].disabled = False
            self.fields['condition'].disabled = False
            self.fields['remarks'].disabled = False
            self.fields['reservation_details'].disabled = False
            self.fields['renewal_history'].disabled = False
    
    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data