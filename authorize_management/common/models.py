from django.db import models
from django.db import models
from decimal import Decimal
from django.db import models

class Student(models.Model):
    student_id = models.AutoField(primary_key=True) 
    # Basic information
    
    full_name = models.CharField(max_length=255)  # Student's full name
    date_of_birth = models.DateField()  # Date of birth
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])  # Gender
    address = models.TextField()  # Home address
    student_class = models.IntegerField()  # Class/Grade
    section = models.CharField(max_length=10, blank=True, null=True)  # Section (optional)
    roll_number = models.IntegerField()  # Roll number
    admission_date = models.DateField()  # Date of admission
    guardian_phone_number = models.IntegerField()  # Contact number
    father_name = models.CharField(max_length=255,blank=True, null=True)  # Father's name
    mother_name = models.CharField(max_length=255,blank=True, null=True)  # Mother's name
    guardian_name = models.CharField(max_length=255)  # Guardian's name (optional)
    occupation_of_parents = models.CharField(max_length=255,null=True)  # Profession of parents
    emergency_contact = models.IntegerField(blank=True,null=True)  # Emergency contact number
    medical_info = models.TextField(blank=True, null=True)  # Known medical conditions, allergies, or special needs
    blood_group = models.CharField(max_length=10)  # Blood group
    attendance_record = models.CharField(max_length=40,blank=True)  # Attendance record (you can add a more structured model later)
    academic_performance = models.CharField(max_length=255,blank=True, null=True)  # Grades or marks
    email = models.EmailField(unique=True)  # Email address
    admission_number = models.IntegerField(unique=True)  # Unique identifier for each student
    additional_info = models.TextField(blank=True, null=True)  # Additional information
    photograph = models.ImageField(upload_to='student_photos/', blank=True, null=True)  # Student photograph
    identification_marks = models.TextField(blank=True, null=True)  # Unique physical identifiers

    def __str__(self):
        return self.admission_number

class FeesHistory(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Overdue', 'Overdue'),
        ('Partially Paid','Partially Paid')
    ]
    
    # Student Information
    student = models.ForeignKey(
        Student,  # Use the imported Student model
        on_delete=models.CASCADE, 
        related_name="fees_history", 
        null=True, 
        blank=True
    )
    feehistory_id = models.AutoField(primary_key=True,unique=True) 
    # Fee Details
    fee_type = models.CharField(max_length=100)  # Type of fee (tuition, library, etc.)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)  # Amount due for the fee type
    due_date = models.DateField()  # Deadline for payment
    
    # Payment Information
    transaction_id = models.CharField(max_length=100, unique=True)  # Unique transaction ID
    payment_date = models.DateField()  # Date of payment
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount paid
    payment_method = models.CharField(max_length=50,blank=True,null=True)  # Mode of payment (cash, cheque, etc.)
    receipt_number = models.IntegerField(unique=True)  # Receipt number

    late_fees = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Late fees applied
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount paid so far

    # Payment Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')  # Current status of payment
    installments = models.TextField(null=True, blank=True)  # Details about installments, if applicable
    scholarships_discounts = models.TextField(null=True, blank=True)  # Scholarships or discounts applied
    # Additional Information
    remarks = models.TextField(null=True, blank=True)  # Any additional comments

    # Method to calculate the balance due based on payment
   
    class Meta:
        unique_together = ('student', 'feehistory_id')  # Enforce unique relationship per student

    def __str__(self):
        return f"{self.student} - {self.fee_type} - {self.status}"

    
class LibraryHistory(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="library_history",
        null=False,
        blank=False
    )
    
    history_id = models.AutoField(primary_key=True,unique=True)  # Unique identifier for each library history record

    book_id = models.IntegerField()
    book_title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, null=True, blank=True)
    publisher = models.CharField(max_length=255, null=True, blank=True)
    isbn = models.CharField(max_length=20, null=True, blank=True)
    genre = models.CharField(max_length=50, null=True, blank=True)
    edition = models.CharField(max_length=50, null=True, blank=True)
    year_of_publication = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=50, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)

    borrowed_date = models.DateField()
    due_date = models.DateField()
    returned_date = models.DateField(null=True)

    STATUS_CHOICES = [
        ("Borrowed", "Borrowed"),
        ("Returned", "Returned"),
        ("Overdue", "Overdue"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Borrowed")

    fines = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    condition = models.TextField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    reservation_details = models.TextField(null=True, blank=True)
    renewal_history = models.TextField(null=True, blank=True)

    librarian_id = models.CharField(max_length=50, null=True, blank=True)
    librarian_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('student', 'history_id')  # Ensure each student can have only one unique history entry

    def __str__(self):
        return f"{self.book_title} ({self.status})"

    def is_editable(self):
        return self.returned_date is None
