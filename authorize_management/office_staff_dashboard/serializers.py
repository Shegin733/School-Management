from rest_framework import serializers
from common.models import Student,FeesHistory
from django.contrib.auth.models import User
from decimal import Decimal
from rest_framework import serializers
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid  # For generating a new unique transaction ID
from datetime import date
from datetime import datetime
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from rest_framework.exceptions import ValidationError


    # Use existing instance data if applicable
def validate_fee_data(data, instance=None):
    payment_amount = data.get("payment_amount")
    total_paid = data.get("total_paid")
    transaction_id = data.get("transaction_id")
    due_date = data.get("due_date")
    payment_date = data.get("payment_date")
    late_fees = data.get("late_fees")
    amount_due = data.get("amount_due")

    if transaction_id:
        existing_record = FeesHistory.objects.filter(transaction_id=transaction_id).first()
        if existing_record:
            raise ValidationError("The transaction ID must be unique.")

    if payment_amount is not None and total_paid:
            amount_due = payment_amount - total_paid
            data["amount_due"]=amount_due

    if total_paid and total_paid < 0:
        raise ValidationError("Payment amount cannot be negative.")

    if total_paid and payment_amount and total_paid > payment_amount:
        raise ValidationError("Actual payment cannot exceed the payment limit.")

    # Calculate updated total_paid (previous + new total_paid)
    if amount_due and total_paid:
          data["status"] = "Partially Paid"
    elif amount_due == 0 and total_paid and total_paid > 0:
        data["status"] = "Paid"
    else:
         data["status"] = "Pending"

    if data.get("status") == "Paid" and data.get("amount_due", Decimal(0)) > 0:
        raise ValidationError("Status cannot be 'Paid' if there is still an amount due.")

    if payment_amount and amount_due and payment_amount < amount_due:
        raise ValidationError("Amount due cannot be greater than the Payment amount.")

    scholarships_discounts = data.get("scholarships_discounts", 0)
    if scholarships_discounts is not None and amount_due:
        try:
            if Decimal(scholarships_discounts) > amount_due:
                raise ValidationError("Scholarships or discounts cannot exceed the amount due.")
        except InvalidOperation:
            raise ValidationError("Invalid format for scholarships or discounts.")

    
    if payment_date:
        try:
            if isinstance(payment_date, str):
                payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
            if payment_date > date.today():
                raise ValidationError("Payment date cannot be in the future.")
        except ValueError:
            raise ValidationError("Invalid date format")

    if due_date and payment_date:
        try:
            if isinstance(payment_date, str):
                payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            if payment_date < due_date:
                raise ValidationError("Payment date cannot be earlier than the due date.")
        except ValueError:
            raise ValidationError("Invalid date format")

    if late_fees is not None and late_fees < 0:
        raise ValidationError("Late fees cannot be negative.")

    
    return data



class FeesHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeesHistory
        fields = '__all__'
        read_only_fields = ['student']

    def validate(self, data):
        validate_fee_data(data, instance=None)
        return data

    def update(self, instance, validated_data):
        validate_fee_data(validated_data, instance=instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance