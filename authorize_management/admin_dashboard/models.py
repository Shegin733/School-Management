from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Office Staff'),
        ('librarian', 'Librarian'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)
    def __str__(self):
        return self.username
    

class Administrator(models.Model):
    # Personal Information
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    address = models.TextField()
    phone_number = models.IntegerField()

    # Professional Information
    employee_id = models.IntegerField(unique=True)
    designation = models.CharField(max_length=100)
    date_of_joining = models.DateField()
    qualifications = models.TextField(blank=True)
    previous_experience = models.TextField(blank=True, null=True)
    supervisor_name = models.CharField(max_length=255, blank=True, null=True)
    
    # Employment Details
    work_schedule = models.TextField(blank=True, null=True)
    attendance_record = models.CharField(max_length=255,blank=True)
    performance_reviews = models.TextField(blank=True)
    job_responsibilities = models.TextField(blank=True)
    salary_details = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    contract_details = models.TextField(blank=True, null=True)
    promotion_hike = models.CharField(max_length=255,blank=True, null=True)
    
    # Administrative Details
    office_location = models.CharField(max_length=255,blank=True)
    key_projects = models.TextField(blank=True, null=True)
    policies_managed = models.TextField(blank=True, null=True)

    # Emergency and Personal Information
    emergency_contact = models.IntegerField(blank=True,null=True)
    medical_info = models.TextField(blank=True, null=True)
    photograph = models.ImageField(upload_to='administrator_photos/',blank=True)
    blood_group = models.CharField(max_length=6,blank=True)

    # Additional Information
    languages_known = models.TextField(blank=True, null=True)
    skills_and_training = models.TextField(blank=True, null=True)
    achievements = models.TextField(blank=True, null=True)
    specializations = models.TextField(blank=True, null=True)  # Areas of expertise
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Administrator"


class OfficeStaff(models.Model):
    # Link to User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='office_staff_profile')
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    address = models.TextField()
    phone_number = models.IntegerField()
    employee_id = models.IntegerField(unique=True)
    supervisor_name = models.CharField(max_length=255, blank=True, null=True)
    # Professional Information
    position = models.CharField(max_length=50)  # Job title or designation
    department = models.CharField(max_length=100)  # Department or section
    date_of_joining = models.DateField()  # Joining date
    qualifications = models.TextField(blank=True)  # Educational qualifications
    previous_experience = models.TextField(blank=True, null=True)  # Previous work experience

    # Employment Details
    work_schedule = models.TextField(blank=True)  # Working hours
    attendance_record = models.TextField(blank=True)  # Attendance and leaves
    performance_reviews = models.TextField(blank=True)  # Performance appraisals
    job_responsibilities = models.TextField(blank=True)  # Assigned responsibilities
    salary_details = models.DecimalField(max_digits=10, decimal_places=2, blank=True,null=True)  # Salary information
    contract_details = models.TextField(blank=True, null=True)  # Contract-related details
    promotion_hike = models.TextField(blank=True, null=True)  # Promotion details
    # Emergency and Personal Information
    emergency_contact = models.CharField(max_length=15, blank=True,null=True)
    medical_info = models.TextField(blank=True, null=True)
    photograph = models.ImageField(upload_to='office_staff_photos/', blank=True)
    blood_group = models.CharField(max_length=10, blank=True)

    # Additional Information
    languages_known = models.TextField(blank=True, null=True)
    skills_and_training = models.TextField(blank=True, null=True)
    specializations = models.TextField(blank=True, null=True)  # Areas of expertise
    projects = models.TextField(blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)
  

    def __str__(self):
        return f"{self.user.username} - {self.position}"


class Librarian(models.Model):
    # Link to User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='librarian_profile')
    #personal info
    # Basic Information
   
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    address = models.TextField()
    employee_id = models.IntegerField(unique=True)
    supervisor_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number=models.IntegerField()
    
    # Library Management Information
    assigned_section = models.CharField(max_length=50)  # Assigned library section
    date_of_joining = models.DateField()  # Joining date
    qualifications = models.TextField(blank=True)  # Educational qualifications
    previous_experience = models.TextField(blank=True, null=True)  # Previous work experience

    # Employment Details
    work_schedule = models.CharField(max_length=50,blank=True, null=True)  # Working hours
    attendance_record = models.CharField(max_length=50,blank=True)  # Attendance
    performance_reviews = models.TextField(blank=True, null=True)  # Performance appraisals
    salary_details = models.DecimalField(max_digits=10, decimal_places=2, blank=True,null=True)  # Salary
    contract_details = models.TextField(blank=True)
    promotion_hike = models.CharField(max_length=50,blank=True, null=True)  # Promotion details
    job_responsibilities = models.TextField(blank=True)

    # Emergency and Personal Information
    emergency_contact = models.CharField(max_length=15, blank=True)
    medical_info = models.TextField(blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True)
    photograph = models.ImageField(upload_to='librarian_photos/', blank=True)

    # Additional Information
    achievements = models.TextField(blank=True, null=True)
    languages_known = models.TextField(blank=True, null=True)
    skills_and_training = models.TextField(blank=True, null=True)
    specializations = models.TextField(blank=True, null=True)  # Areas of expertise
   
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Librarian"


