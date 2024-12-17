from rest_framework import serializers
from common.models import Student,FeesHistory
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
import re
from admin_dashboard.models import User
from django.core.exceptions import ValidationError
from datetime import timedelta
from datetime import datetime
# Forgot Password Serializer
def validate_student_data(data,instance=None):
    phone_number = data.get('guardian_phone_number')
    emergency_contact = data.get('emergency_contact')

    if phone_number or emergency_contact:
        phone_number = str(phone_number) if phone_number else ''
        emergency_contact = str(emergency_contact) if emergency_contact else ''

    if phone_number and (not phone_number.isdigit() or len(phone_number) not in [10, 12]):
        raise ValidationError({'phone_number': 'Invalid phone number. Must be 10 or 12 digits.'})

    if emergency_contact and (not emergency_contact.isdigit() or len(emergency_contact) not in [10, 12]):
        raise ValidationError({'emergency_contact': 'Invalid emergency contact number. Must be 10 or 12 digits.'})

    date_of_birth = data.get('date_of_birth')
    admission_date = data.get('admission_date')

    if date_of_birth and admission_date:
        try:
            if isinstance(date_of_birth, str):
                date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()

            if isinstance(admission_date, str):
                admission_date = datetime.strptime(admission_date, '%Y-%m-%d').date()

        except ValueError:
            raise ValidationError({'date_of_birth': 'Invalid date format. Use YYYY-MM-DD.'})

        age_at_admission = (admission_date - date_of_birth).days // 365
        if age_at_admission < 4:
            raise ValidationError({'admission_date': 'Admission date must be at least 4 years after date of birth.'})

    attendance_record = data.get("attendance_record")
    academic_performance = data.get("academic_performance")

    if not attendance_record and academic_performance:
        raise ValidationError("If attendance record is not provided, academic performance cannot be updated.")

    section = data.get("section")
    roll_number = data.get("roll_number")
    student_id = data.get("student_id")
    student_class = data.get("student_class")

    if section:
        if Student.objects.filter(section=section, roll_number=roll_number).exclude(student_id=student_id).exists():
            raise ValidationError(f"Roll number {roll_number} already exists in section {section}.")
    else:
        if Student.objects.filter(student_class=student_class, roll_number=roll_number).exclude(student_id=student_id).exists():
            raise ValidationError(f"Roll number {roll_number} already exists in class {student_class}.")

    if admission_date:
        try:
            if isinstance(admission_date, str):
                admission_date = datetime.strptime(admission_date, '%Y-%m-%d').date()

        except ValueError:
            raise ValidationError({'admission_date': 'Invalid date format. Use YYYY-MM-DD.'})

    if admission_date == datetime.today().date():
        if attendance_record and attendance_record.strip() != "":
            raise ValidationError({'attendance_record': 'Attendance record cannot be added if date of joining is today.'})

        if academic_performance and academic_performance.strip() != "":
            raise ValidationError("Academic performance cannot be updated on the day of admission.")
    return data
class PasswordForgotSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """
        Validate that the email is registered with a service provider.
        """
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is not registered with any service provider.")
        return value


# Set New Password Serializer
class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate_new_password(self, value):
        """
        Use Django's password validators and custom rules for password complexity.
        """
        # Validate using Django's built-in validators
        validate_password(value)

        # Custom validation for password complexity
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def validate(self, attrs):
        """
        Ensure that the new password and confirm password match.
        """
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

    # Custom validation logic for the entire data object
    def validate(self, data):
        # If it's an update, pass the instance to validate the existing object
        instance = getattr(self, 'instance', None)
        validate_student_data(data, instance)
        return data

    # Override create method if needed
    def create(self, validated_data):
        student = Student.objects.create(**validated_data)
        return student

    # Override update method if needed
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if value is not None:
                setattr(instance, attr, value)
        instance.save()
        return instance


class StudentDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__' 
    def validate(self, data):
        validate_student_data(data)
        return data
    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    role = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        role = attrs.get('role')
        email = attrs.get('email')
        password = attrs.get('password')

        if not username or not role or not email or not password:
            raise serializers.ValidationError('All fields are required.')

        return attrs
