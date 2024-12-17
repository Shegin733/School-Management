from django.contrib import admin
from common.models import Student,LibraryHistory,FeesHistory
from admin_dashboard.models import User, OfficeStaff, Librarian,Administrator

from django.contrib import admin

class LibraryHistoryAdmin(admin.ModelAdmin):

    def admission_number(self, obj):
        return obj.student.admission_number  # Get admission_number from the Student model

    admission_number.admin_order_field = 'student__admission_number'  # Allow ordering by admission_number
    admission_number.short_description = 'Admission Number'  # Column name in admin

# Register the model with the custom admin class
admin.site.register(LibraryHistory, LibraryHistoryAdmin)

@admin.register(FeesHistory)
class FeesHistoryAdmin(admin.ModelAdmin):
    # Customization for FeesHistory model
    pass
@admin.register(User)
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    # Customization for Student model
    pass
@admin.register(Administrator)
class AdministratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id','designation')
    search_fields = ('user__username', 'email', 'employee_id')
    list_filter = ( 'employee_id',)

@admin.register(OfficeStaff)
class OfficeStaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'created_at')
    search_fields = ('user__username', 'user__email', 'position')
    list_filter = ('created_at',)

@admin.register(Librarian)
class LibrarianAdmin(admin.ModelAdmin):
    list_display = ('user', 'assigned_section', 'created_at')
    search_fields = ('user__username', 'user__email', 'assigned_section')
    list_filter = ('created_at',)





