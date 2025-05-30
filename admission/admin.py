from django.contrib import admin

# Register your models here.


from django.contrib import admin
from .models import *

# Register your models here.

# Admission Notice Admin
class AdmissionNoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'ordering_number', 'active')
    search_fields = ('title',)
    ordering = ('ordering_number',)

admin.site.register(AdmissionNotice, AdmissionNoticeAdmin)


class IntakeAdmin(admin.ModelAdmin):
    list_display = [
        'Program_name', 'intake_name', 'degree_name', 'batch_name', 
        'start_date', 'end_date', 'admit_download', 'admission_test', 
        'result_publish', 'merit_list_admission', 'waiting_list_admission', 
        'orientation', 'coordinator_signature', 'is_open', 'create_at'
    ]
    list_filter = ['is_open', 'intake_name']
    search_fields = ['intake_name']
    ordering = ('-create_at',)

admin.site.register(Intake, IntakeAdmin)


class PersonalInformationAdmin(admin.ModelAdmin):
    list_display = ("applicant", "father_name", "mother_name", "date_of_birth", "sex", "religion", "blood_group", "nationality", "create_at")
    search_fields = ("applicant__full_name", "father_name", "mother_name", "national_id")
    list_filter = ("sex", "religion", "blood_group", "nationality")

admin.site.register(PersonalInformation, PersonalInformationAdmin)



class AcademicQualificationAdmin(admin.ModelAdmin):
    list_display = (
        'applicant', 
        'ssc_exam', 'ssc_board', 'ssc_roll', 'ssc_result_type', 'ssc_result', 'ssc_passing_year',
        'hsc_exam', 'hsc_board', 'hsc_roll', 'hsc_result_type', 'hsc_result', 'hsc_passing_year',
        'graduation_exam', 'graduation_subject', 'graduation_university', 'graduation_result_type', 
        'graduation_result', 'graduation_passing_year',
        'post_graduation_exam', 'post_graduation_subject', 'post_graduation_university', 
        'post_graduation_result_type', 'post_graduation_result', 'post_graduation_passing_year',
        'create_at',
    )

admin.site.register(AcademicQualification, AcademicQualificationAdmin)



class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'applicant', 'applicant_image', 'applicant_sig', 'create_at')

admin.site.register(Photo, PhotoAdmin)



class PaymentAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'transaction_id', 'amount', 'payment_method', 'status', 'applicant__intake', 'created_at')
    list_filter = ('status', 'applicant__intake', 'payment_method', 'created_at')
    search_fields = ('applicant__full_name', 'transaction_id')
    ordering = ('-created_at',)

admin.site.register(Payment, PaymentAdmin)


class StartingRollAdmin(admin.ModelAdmin):
    list_display =('intake', 'starting_number', 'created_at')
admin.site.register(StartingRoll, StartingRollAdmin)


class ResultPrepareAdmin(admin.ModelAdmin):
    # Show important fields in the list view
    list_display = ('id', 'applicant_roll_number', 'applicant', 'category', 'mcq_marks', 'job_marks', 'academic_marks', 'total_marks', )
    
    search_fields = ('applicant__roll_number', 'applicant__full_name',)
    
    # Make `roll_number` accessible in the list view by creating a custom method
    def applicant_roll_number(self, obj):
        return obj.applicant.roll_number
    applicant_roll_number.short_description = 'Roll Number'  # Change the column title in the admin panel

    # Add filtering options
    list_filter = ('category',)
    
    # Make some fields readonly
    readonly_fields = ('total_marks', 'academic_marks')
    
    # Sort by category and then by total_marks in descending order within the same category
    ordering = ('category', '-total_marks')

    # Override save method to auto-calculate academic and total marks
    def save_model(self, request, obj, form, change):
        # Auto-calculate academic_marks and total_marks before saving
        obj.academic_marks = obj.calculate_academic_marks()
        obj.total_marks = obj.mcq_marks + obj.job_marks + obj.academic_marks
        super().save_model(request, obj, form, change)

admin.site.register(ResultPrepare, ResultPrepareAdmin)




class MainGalleryAdmin(admin.ModelAdmin):
    list_display = ('position', 'heading', 'description', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('heading', 'description')
    list_filter = ('created_at',)
    ordering = ('position',)  
admin.site.register(MainGallery, MainGalleryAdmin)


class HomeContentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'chairman', 'chairman_image', 'co_ordinator', 'co_ordinato_image',
        'founded', 'faculties', 'students', 'passed_students', 'created_at', 'updated_at'
    )
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('chairman__full_name', 'co_ordinator__full_name')
    list_filter = ('created_at',)


admin.site.register(HomeContent, HomeContentAdmin)
