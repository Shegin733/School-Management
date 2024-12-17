# forms.py
from django import forms
from django.core.exceptions import ValidationError
from common.models import FeesHistory
from django.utils import timezone
from django import forms
from common.models import FeesHistory
from decimal import Decimal
# forms.py
from .serializers import validate_fee_data  # Import the validation function

class FeesHistoryForm(forms.ModelForm):
    class Meta:
        model = FeesHistory
        fields = [
             'fee_type', 'amount_due', 'due_date', 'transaction_id',
            'payment_date', 'payment_amount', 'payment_method', 'receipt_number',
            'late_fees', 'total_paid', 'status', 'installments',
             'remarks'
        ]
       

    def __init__(self, *args, **kwargs):
        self.partial = kwargs.pop('partial', False)
        super().__init__(*args, **kwargs)

        if self.partial:
            for field in self.fields.values():
                field.required = False

    def clean(self):
        cleaned_data = super().clean()

        # Call the external validation function
        try:
            cleaned_data = validate_fee_data(cleaned_data)
        except ValidationError as e:
            # Handling validation errors
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        self.add_error(field, error)
            else:
                # If it's a general validation error, add it as a non-field error
                self.add_error(None, str(e))

        return cleaned_data
