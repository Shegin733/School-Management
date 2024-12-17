from rest_framework import serializers
from .models import User
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Administrator, OfficeStaff, Librarian
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db.models import Q
from datetime import datetime
from rest_framework.exceptions import ValidationError
from .models import OfficeStaff, Administrator, Librarian

def validate_common_fields(data):
    phone_number = data.get('phone_number')
    emergency_contact = data.get('emergency_contact')
    employee_id = data.get('employee_id')

    if phone_number:
        if isinstance(phone_number, tuple):
            phone_number = phone_number[0]
        if isinstance(phone_number, int):
            phone_number = str(phone_number)
        phone_number = phone_number.strip()
        if not phone_number.isdigit() or len(phone_number) not in [10, 12]:
            raise ValidationError({'phone_number': 'Invalid phone number. Must be 10 or 12 digits.'})

        if (OfficeStaff.objects.filter(phone_number=phone_number).exists() or
            Administrator.objects.filter(phone_number=phone_number).exists() or
            Librarian.objects.filter(phone_number=phone_number).exists()):
            raise ValidationError({'phone_number': 'Phone number must be unique across all models.'})

    if employee_id:
        employee_id = str(employee_id).strip()
        if (OfficeStaff.objects.filter(employee_id=employee_id).exists() or
            Administrator.objects.filter(employee_id=employee_id).exists() or
            Librarian.objects.filter(employee_id=employee_id).exists()):
            raise ValidationError({'employee_id': 'Employee ID must be unique across all models.'})

    if emergency_contact:
        emergency_contact = str(emergency_contact).strip()
        if not emergency_contact.isdigit() or len(emergency_contact) not in [10, 12]:
            raise ValidationError({'emergency_contact': 'Invalid emergency contact number. Must be 10 or 12 digits.'})

    date_of_birth = data.get('date_of_birth')
    date_of_joining = data.get('date_of_joining')

    if date_of_birth and date_of_joining:
        try:
            if isinstance(date_of_birth, str):
                date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            if isinstance(date_of_joining, str):
                date_of_joining = datetime.strptime(date_of_joining, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError({'date_of_birth': 'Invalid date format. Use YYYY-MM-DD.'})

        age_at_joining = (date_of_joining - date_of_birth).days // 365
        if age_at_joining < 18:
            raise ValidationError({'date_of_joining': 'Date of joining must be at least 18 years after date of birth.'})

    if date_of_joining :
        try:
            if isinstance(date_of_joining, str):
                date_of_joining = datetime.strptime(date_of_joining, '%Y-%m-%d').date()
            if date_of_joining > datetime.now().date():
             raise ValidationError({'date_of_joining': 'Date of joining cannot be in the future.'})
        except ValueError:
            raise ValidationError({'date_of_birth': 'Invalid date format. Use YYYY-MM-DD.'})

    attendance_record = data.get('attendance_record')
    if not attendance_record or attendance_record.strip() == "":
        restricted_fields = ['performance_review', 'promotion_hike', 'key_projects']
        for field in restricted_fields:
            if data.get(field):
                raise ValidationError({field: f'{field} cannot be set if attendance_record is null or blank.'})

    if date_of_joining and date_of_joining == datetime.now().date():
        restricted_fields = ['performance_review', 'promotion_hike', 'key_projects']
        for field in restricted_fields:
            if data.get(field):
                raise ValidationError({field: f'{field} cannot be set if date_of_joining is today.'})

        if attendance_record and attendance_record.strip() != "":
            raise ValidationError({'attendance_record': 'Attendance record cannot be added if date of joining is today.'})

class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrator
        fields = '__all__'
    def validate(self, data):
        validate_common_fields(data)
        return data
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if value is not None:
                setattr(instance, attr, value)
        instance.save()
        return instance

class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeStaff
        fields = '__all__'
    def validate(self, data):
        validate_common_fields(data)
        return data
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if value is not None:
                setattr(instance, attr, value)
        instance.save()
        return instance

class LibrarianProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Librarian
        fields = '__all__'
    def validate(self, data):
        validate_common_fields(data)
        return data
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)  # Make `first_name` required
    is_staff = serializers.BooleanField(required=True)
    is_active = serializers.BooleanField(required=True)
    
    class Meta:
        model = User
        fields = '__all__'

    def validate(self, data):
        validate_common_fields(data)
        return data
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)  # Make `first_name` required
    is_staff = serializers.BooleanField(required=True)
    is_active = serializers.BooleanField(required=True)
    
    class Meta:
        model = User
        fields = '__all__'

    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
