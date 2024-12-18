from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from common.models import Student
from .serializers import FeesHistorySerializer,validate_fee_data
from admin_dashboard.permissions import IsAdminOrOfficeStaff,IsAdmin,IsOfficeStaff
from django.shortcuts import get_object_or_404
from .forms import  FeesHistoryForm
from rest_framework.decorators import action
from common.models import FeesHistory
from common.serializers import StudentSerializer
from django.core.exceptions import ValidationError
# ViewSet for CRUD operations on Fees (Only OfficeAccount or Admin can perform CRUD)

class FeesHistoryViewSet(viewsets.ViewSet):
    permission_classes = [IsAdmin|IsOfficeStaff]

    def list(self, request):
        fees_histories = FeesHistory.objects.all()
        serializer = FeesHistorySerializer(fees_histories, many=True)
        return Response(serializer.data)

    def retrieve_by_student(self, request, student_id=None):
        student = get_object_or_404(Student, student_id=student_id)
        fees_histories = FeesHistory.objects.filter(student=student)
        serializer = FeesHistorySerializer(fees_histories, many=True)
        return Response(serializer.data)

    def retrieve_by_history_and_student(self, request, student_id=None, feehistory_id=None):
        student = get_object_or_404(Student, student_id=student_id)
        fees_history = get_object_or_404(FeesHistory, pk=feehistory_id, student=student)
        serializer = FeesHistorySerializer(fees_history)
        return Response(serializer.data)

    def create(self, request, student_id=None, *args, **kwargs):
        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            return Response({"message": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            validated_data = validate_fee_data(request.data)
        except ValidationError as e:
            error_details = {
                "message": "Validation error occurred.",
                "errors": e.message_dict if hasattr(e, "message_dict") else str(e)
            }
            return Response(error_details, status=status.HTTP_400_BAD_REQUEST)

        serializer = FeesHistorySerializer(data=validated_data)

        if serializer.is_valid():
            serializer.save(student=student)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, student_id=None, pk=None):
        student = get_object_or_404(Student, student_id=student_id)
        fees_history = get_object_or_404(FeesHistory, pk=pk, student=student)
       
        try:
            validated_data = validate_fee_data(request.data, instance=fees_history)
        except ValidationError as e:
            error_details = {
                "message": "Validation error occurred.",
                "errors": e.message_dict if hasattr(e, "message_dict") else str(e)
            }
            return Response(error_details, status=status.HTTP_400_BAD_REQUEST)
        try:
            validated_data = validate_fee_data(request.data, instance=fees_history)
        except ValidationError as e:
            error_details = {
                "message": "Validation error occurred.",
                "errors": e.message_dict if hasattr(e, "message_dict") else str(e)
            }
            return Response(error_details, status=status.HTTP_400_BAD_REQUEST)
        if validated_data is None:
            return Response({"message": "Invalid data received."}, status=status.HTTP_400_BAD_REQUEST)
        if "total_paid" not in validated_data:
            validated_data["total_paid"] = fees_history.total_paid
        previous_total_paid = fees_history.total_paid
        previous_amount_due = fees_history.amount_due
        total_paid = validated_data.get("total_paid", previous_total_paid)
        updated_total_paid = previous_total_paid + total_paid if total_paid else previous_total_paid
        payment_amount = validated_data.get("payment_amount", fees_history.payment_amount)
        if payment_amount:
            updated_amount_due = payment_amount - updated_total_paid
            if updated_amount_due < 0:
                updated_amount_due = 0  # Avoid negative amounts
            if updated_amount_due == 0 and updated_total_paid > 0:
                validated_data["status"] = "Paid"
            else:
                validated_data["amount_due"] = updated_amount_due

        if updated_total_paid > 0 and updated_amount_due > 0:
            validated_data["status"] = "Partially Paid"
        elif updated_total_paid == 0:
            validated_data["status"] = "Pending"
        elif updated_amount_due == 0:
            validated_data["status"] = "Paid"
            # Step 2: Check for total_paid in the validated_data
        if "total_paid" not in validated_data:
            validated_data["total_paid"] = fees_history.total_paid
            return Response({"message": "'total_paid' is required in the data."}, status=status.HTTP_400_BAD_REQUEST)

        
        serializer = FeesHistorySerializer(fees_history, data=validated_data, partial=True)
        if serializer.is_valid():
            for field, value in validated_data.items():
                if value is None:
                    validated_data[field] = getattr(fees_history, field)

            payment_amount = validated_data.get("payment_amount", fees_history.payment_amount)
            total_paid = validated_data.get("total_paid", fees_history.total_paid)
            if payment_amount is not None and total_paid is not None:
                updated_amount_due = payment_amount - total_paid
                if updated_amount_due < 0:
                    updated_amount_due = 0

                validated_data["amount_due"] = updated_amount_due
            serializer = FeesHistorySerializer(fees_history, data=validated_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            

    def destroy(self, request, student_id=None, pk=None):
        confirm = request.query_params.get('confirm', None)
        if confirm != 'true':
            return Response("Please confirm the deletion by adding '?confirm=true' to the request.")
        student = get_object_or_404(Student, student_id=student_id)
        fees_history = get_object_or_404(FeesHistory, pk=pk, student=student)
        fees_history.delete()
        return Response({"message": "Fees history record deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, student_id=None, pk=None):
        student = get_object_or_404(Student, student_id=student_id)
        fees_history = get_object_or_404(FeesHistory, pk=pk, student=student)

        if fees_history.status == 'Paid':
            return Response({"message": "This record has already been marked as paid."}, status=status.HTTP_400_BAD_REQUEST)
        form = FeesHistoryForm(request.data, instance=fees_history, partial=True)
        update_data = request.data
        for field in fees_history._meta.fields:
            field_name = field.name
            if field_name not in update_data:
                update_data[field_name] = getattr(fees_history, field_name)

        try:
            validate_fee_data(update_data)
        except ValidationError as e:
            error_details = {
                "message": "Validation error occurred.",
                "errors": e.message_dict if hasattr(e, "message_dict") else str(e)
            }
            return Response(error_details, status=status.HTTP_400_BAD_REQUEST)

        if form.is_valid():
            form.save()

            updated_fees_history = FeesHistorySerializer(fees_history)

            return Response({
                'message': 'Status updated successfully.',
                'data': updated_fees_history.data
            }, status=status.HTTP_200_OK)

        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)