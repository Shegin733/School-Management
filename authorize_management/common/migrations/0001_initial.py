# Generated by Django 5.1.1 on 2024-12-17 14:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('student_id', models.AutoField(primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=255)),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10)),
                ('address', models.TextField()),
                ('student_class', models.IntegerField()),
                ('section', models.CharField(blank=True, max_length=10, null=True)),
                ('roll_number', models.IntegerField()),
                ('admission_date', models.DateField()),
                ('guardian_phone_number', models.IntegerField()),
                ('father_name', models.CharField(blank=True, max_length=255, null=True)),
                ('mother_name', models.CharField(blank=True, max_length=255, null=True)),
                ('guardian_name', models.CharField(max_length=255)),
                ('occupation_of_parents', models.CharField(max_length=255, null=True)),
                ('emergency_contact', models.IntegerField(blank=True, null=True)),
                ('medical_info', models.TextField(blank=True, null=True)),
                ('blood_group', models.CharField(max_length=10)),
                ('attendance_record', models.CharField(blank=True, max_length=40)),
                ('academic_performance', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('admission_number', models.IntegerField(unique=True)),
                ('additional_info', models.TextField(blank=True, null=True)),
                ('photograph', models.ImageField(blank=True, null=True, upload_to='student_photos/')),
                ('identification_marks', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LibraryHistory',
            fields=[
                ('history_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('book_id', models.CharField(max_length=50)),
                ('book_title', models.CharField(max_length=255)),
                ('author', models.CharField(blank=True, max_length=255, null=True)),
                ('publisher', models.CharField(blank=True, max_length=255, null=True)),
                ('isbn', models.CharField(blank=True, max_length=20, null=True)),
                ('genre', models.CharField(blank=True, max_length=50, null=True)),
                ('edition', models.CharField(blank=True, max_length=50, null=True)),
                ('year_of_publication', models.IntegerField(blank=True, null=True)),
                ('language', models.CharField(blank=True, max_length=50, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('borrowed_date', models.DateField()),
                ('due_date', models.DateField()),
                ('returned_date', models.DateField(null=True)),
                ('status', models.CharField(choices=[('Borrowed', 'Borrowed'), ('Returned', 'Returned'), ('Overdue', 'Overdue')], default='Borrowed', max_length=20)),
                ('fines', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('condition', models.TextField(blank=True, null=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('reservation_details', models.TextField(blank=True, null=True)),
                ('renewal_history', models.TextField(blank=True, null=True)),
                ('librarian_id', models.CharField(blank=True, max_length=50, null=True)),
                ('librarian_name', models.CharField(blank=True, max_length=255, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='library_history', to='common.student')),
            ],
            options={
                'unique_together': {('student', 'history_id')},
            },
        ),
        migrations.CreateModel(
            name='FeesHistory',
            fields=[
                ('feehistory_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('fee_type', models.CharField(max_length=100)),
                ('amount_due', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('due_date', models.DateField()),
                ('transaction_id', models.CharField(max_length=100, unique=True)),
                ('payment_date', models.DateField()),
                ('payment_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(blank=True, max_length=50, null=True)),
                ('receipt_number', models.IntegerField(unique=True)),
                ('late_fees', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_paid', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('Paid', 'Paid'), ('Pending', 'Pending'), ('Overdue', 'Overdue'), ('Partially Paid', 'Partially Paid')], default='Pending', max_length=20)),
                ('installments', models.TextField(blank=True, null=True)),
                ('scholarships_discounts', models.TextField(blank=True, null=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fees_history', to='common.student')),
            ],
            options={
                'unique_together': {('student', 'feehistory_id')},
            },
        ),
    ]