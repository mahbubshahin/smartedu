
# Create your models here.


from django.db import models, transaction
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
# Create your models here.
from accounts.models import UserRegistration
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from django.core.files.images import get_image_dimensions


from django.db import transaction

from django.db import models
from django.utils import timezone
import os
from django.db.models.signals import post_delete
from django.dispatch import receiver


class AdmissionNotice(models.Model):
    title = models.CharField(max_length=200)  
    pdf_file = models.FileField(upload_to='admission_notice')  
    ordering_number = models.PositiveIntegerField()
    active = models.BooleanField(default=False)  
    create_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['ordering_number']  

    def __str__(self):
        return self.title




class Intake(models.Model):
    Program_name = models.CharField(max_length=200)
    intake_name = models.CharField(max_length=255)
    degree_name = models.CharField(max_length=255, blank=True, null=True)
    batch_name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    admit_download = models.DateTimeField()
    admission_test = models.DateTimeField()
    result_publish = models.DateField()
    merit_list_admission = models.CharField(max_length=100, blank=True, null=True)
    waiting_list_admission = models.CharField(max_length=100, blank=True, null=True)
    orientation = models.DateField()
    is_open = models.BooleanField(default=False)
    create_at = models.DateTimeField(default=timezone.now)
    
    coordinator_signature = models.ImageField(
        upload_to='coordinator_signatures/', 
        blank=True, 
        null=True
    )

    def is_application_open(self):
        now = timezone.now()
        return self.is_open and self.start_date <= now <= self.end_date

    def save(self, *args, **kwargs):
        try:
            old_instance = Intake.objects.get(pk=self.pk)
            if old_instance.coordinator_signature and self.coordinator_signature != old_instance.coordinator_signature:
                if os.path.isfile(old_instance.coordinator_signature.path):
                    os.remove(old_instance.coordinator_signature.path)
        except Intake.DoesNotExist:
            pass  # No previous file to delete

        super().save(*args, **kwargs)

    def __str__(self):
        return self.intake_name



class StartingRoll(models.Model):
    intake = models.OneToOneField(Intake, on_delete=models.CASCADE)
    starting_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.intake.batch_name} - {self.starting_number}"





class PersonalInformation(models.Model):

    SEX_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
    ]

    RELIGION_CHOICES = [
        ("Islam", "Islam"),
        ("Hinduism", "Hinduism"),
        ("Christianity", "Christianity"),
        ("Buddhism", "Buddhism"),
        ("Other", "Other"),
    ]

    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("O+", "O+"),
        ("O-", "O-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
    ]

    NATIONALITY_CHOICES = [
        ("Bangladesh", "Bangladesh"),
        ("Others", "Others"),
    ]

    applicant = models.OneToOneField(UserRegistration, on_delete=models.CASCADE, related_name="personal_info", )
    father_name = models.CharField(max_length=200,blank=True,null=True,)
    mother_name = models.CharField(max_length=200, blank=True,null=True,)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, blank=True,null=True,)
    religion = models.CharField(max_length=25, choices=RELIGION_CHOICES, blank=True,null=True,)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True,null=True,)
    nationality = models.CharField(max_length=50, choices=NATIONALITY_CHOICES,blank=True,null=True, )
    national_id = models.CharField(max_length=20, blank=True, null=True)
    present_address = models.TextField(blank=True,null=True,)
    permanent_address = models.TextField(blank=True,null=True,)
    create_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True) 
    def __str__(self):
        return f"{self.applicant.full_name} - Personal Info"


    @staticmethod
    def get_personal_all_choices():
        """
        To show dynamic data from model to template
        """
        return {
            "sex_choice": PersonalInformation.SEX_CHOICES,
            "religion_choice": PersonalInformation.RELIGION_CHOICES,
            "blood_group_choice": PersonalInformation.BLOOD_GROUP_CHOICES,
            "nationality_choice": PersonalInformation.NATIONALITY_CHOICES,
        }




class AcademicQualification(models.Model):

    SSC_EXAM_CHOICES = [
        ("SSC", "SSC"),
        ("Dakhil", "Dakhil"),
        ("SSC Vocational", "SSC Vocational"),
        ("O Level/Cambridge", "O Level/Cambridge"),
        ("SSC Equivalent", "SSC Equivalent"),
    ]

    SSC_BOARD_CHOICES = [
        ("Dhaka", "Dhaka"),
        ("Comilla", "Comilla"),
        ("Rajshahi", "Rajshahi"),
        ("Jessore", "Jessore"),
        ("Chittagong", "Chittagong"),
        ("Barisal", "Barisal"),
        ("Sylhet", "Sylhet"),
        ("Dinajpur", "Dinajpur"),
        ("Madrasah", "Madrasah"),
        ("Technical", "Technical"),
        ("Cambridge International - IGCSE", "Cambridge International - IGCSE"),
        ("Edexcel International", "Edexcel International"),
        ("Others", "Others"),
    ]

    
    
    RESULT_TYPE_CHOICES = [
        ("1st Class", "1st Class"),
        ("2nd Class", "2nd Class"),
        ("GPA (out of 4)", "GPA (out of 4)"),
        ("GPA (out of 5)", "GPA (out of 5)"),
    ]


    SSC_GROUP_CHOICES = [
        ("Science", "Science"),
        ("Humanities", "Humanities"),
        ("Business Studies", "Business Studies"),
        ("Others", "Others"),
    ]
    

    current_year = datetime.now().year
    start_year = current_year - 40
    SSC_PASSING_YEAR_CHOICES = [(year, str(year)) for year in range(start_year, current_year + 1)]

    
     # HSC Exam Choices
    HSC_EXAM_CHOICES = [
        ("HSC", "HSC"),
        ("Alim", "Alim"),
        ("Business Management", "Business Management"),
        ("Diploma in Engineering/Agriculture", "Diploma in Engineering/Agriculture"),
        ("A Level/Sr. Cambridge", "A Level/Sr. Cambridge"),
        ("H.S.C Equivalent", "H.S.C Equivalent"),
    ]

    HSC_BOARD_CHOICES = [
        ("Dhaka", "Dhaka"),
        ("Comilla", "Comilla"),
        ("Rajshahi", "Rajshahi"),
        ("Jessore", "Jessore"),
        ("Chittagong", "Chittagong"),
        ("Barisal", "Barisal"),
        ("Sylhet", "Sylhet"),
        ("Dinajpur", "Dinajpur"),
        ("Madrasah", "Madrasah"),
        ("Technical", "Technical"),
        ("Cambridge International - IGCSE", "Cambridge International - IGCSE"),
        ("Edexcel International", "Edexcel International"),
        ("Others", "Others"),
    ]

    HSC_RESULT_TYPE_CHOICES = [
        ("1st Class", "1st Class"),
        ("2nd Class", "2nd Class"),
        ("GPA (out of 4)", "GPA (out of 4)"),
        ("GPA (out of 5)", "GPA (out of 5)"),
    ]


    HSC_GROUP_CHOICES = [
        ("Science", "Science"),
        ("Humanities", "Humanities"),
        ("Business Studies", "Business Studies"),
        ("Others", "Others"),
    ]

    HSC_PASSING_YEAR_CHOICES = [(year, str(year)) for year in range(start_year, current_year + 1)]

    # Graduation Level
    GRADUATION_EXAM_CHOICES = [
    ("Bachelor Degree (Science Background)", "Bachelor Degree (Science Background)"),
    ("Bachelor Degree (Arts Background)", "Bachelor Degree (Arts Background)"),
    ("Bachelor Degree (Commerce Background)", "Bachelor Degree (Commerce Background"),
    ("Bachelor Degree (Engineering Background)", "Bachelor Degree (Engineering Background)"),
    ("Bachelor Degree (Others Background)", "Bachelor Degree (Others Background)"),]


    GRADUATION_RESULT_TYPE_CHOICES = [
        ("1st Class", "1st Class"),
        ("2nd Class", "2nd Class"),
        ("GPA (out of 4)", "GPA (out of 4)"),
        ("GPA (out of 5)", "GPA (out of 5)"),
        ("Pass", "Pass"),
    ]

    GRADUATION_PASSING_YEAR_CHOICE = [(year, str(year)) for year in range(start_year, current_year + 1)]

    GRADUATION_COURSE_DUARATION_CHOICE= [
    ("3", "3"),
    ("4", "4"),
    ("5", "5"),
    ]

    # POST Graduation Level
    POST_GRADUATION_EXAM_CHOICES = [
    ("Master Degree (Science Background)", "Master Degree (Science Background)"),
    ("Master Degree (Arts Background)", "Master Degree (Arts Background)"),
    ("Master Degree (Commerce Background)", "Master Degree (Commerce Background"),
    ("Master Degree (Engineering Background)", "Master Degree (Engineering Background)"),
    ("Master Degree (Others Background)", "Master Degree (Others Background)"),]


    POST_GRADUATION_RESULT_TYPE_CHOICES = [
        ("1st Class", "1st Class"),
        ("2nd Class", "2nd Class"),
        ("GPA (out of 4)", "GPA (out of 4)"),
        ("GPA (out of 5)", "GPA (out of 5)"),
        ("Pass", "Pass"),
    ]

    POST_GRADUATION_PASSING_YEAR = [(year, str(year)) for year in range(start_year, current_year + 1)]

    POST_GRADUATION_COURSE_DUARATION= [
    ("1", "1"),
    ("1.5", "1.5"),
    ("2", "2"),
    ("3", "3"),
    ]

    applicant = models.OneToOneField(UserRegistration, on_delete=models.CASCADE, related_name="academic_qualification", )
    
    # SSC or Equivalent
    ssc_exam = models.CharField(max_length=50,choices=SSC_EXAM_CHOICES,blank=True,null=True,verbose_name="SSC Examination")
    ssc_board = models.CharField(max_length=50,choices=SSC_BOARD_CHOICES,blank=True,null=True,verbose_name="SSC Board")
    ssc_roll = models.CharField(max_length=20, blank=True, null=True)
    ssc_result_type = models.CharField(max_length=20,choices=RESULT_TYPE_CHOICES,blank=True,null=True,verbose_name="SSC Result Type")
    ssc_result = models.DecimalField(max_digits=4,decimal_places=2,validators=[MinValueValidator(1.00),MaxValueValidator(9.99)],blank=True,null=True,verbose_name="SSC GPA")
    ssc_group = models.CharField(max_length=20,choices=SSC_GROUP_CHOICES,blank=True,null=True,verbose_name="SSC Group")
    ssc_passing_year = models.IntegerField(choices=SSC_PASSING_YEAR_CHOICES,blank=True,null=True)

    # HSC or Equivalent
    hsc_exam = models.CharField(max_length=50, choices=HSC_EXAM_CHOICES, blank=True, null=True)
    hsc_board = models.CharField(max_length=50, choices=HSC_BOARD_CHOICES, blank=True, null=True)
    hsc_roll = models.CharField(max_length=20, blank=True, null=True)
    hsc_result_type = models.CharField(max_length=50,choices=HSC_RESULT_TYPE_CHOICES, blank=True, null=True)
    hsc_result = models.DecimalField(max_digits=4,decimal_places=2,validators=[MinValueValidator(1.00),MaxValueValidator(9.99)],blank=True,null=True,verbose_name="HSC GPA")
    hsc_group = models.CharField(max_length=50, blank=True, null=True, choices=HSC_GROUP_CHOICES,)
    hsc_passing_year = models.IntegerField(choices=SSC_PASSING_YEAR_CHOICES, blank=True, null=True)

    # Graduation Level
    graduation_exam = models.CharField(max_length=200,choices=GRADUATION_EXAM_CHOICES, blank=True, null=True)
    graduation_subject = models.CharField(max_length=100, blank=True, null=True)
    graduation_university = models.CharField(max_length=100, blank=True, null=True)
    graduation_result_type = models.CharField(max_length=100, choices=GRADUATION_RESULT_TYPE_CHOICES, blank=True, null=True)
    graduation_result = models.DecimalField(max_digits=4,decimal_places=2,validators=[MinValueValidator(1.00),MaxValueValidator(9.99)],blank=True,null=True,verbose_name="Honors CGPA")
    graduation_passing_year = models.IntegerField(choices=GRADUATION_PASSING_YEAR_CHOICE, blank=True, null=True)
    graduation_course_duration = models.CharField(choices=GRADUATION_COURSE_DUARATION_CHOICE,max_length=20, blank=True, null=True)
    graduation_certificate = models.FileField(upload_to='certificates/',blank=True, null=True)
    graduation_transcript = models.FileField(upload_to='transcripts/',blank=True,null=True)


    # Post-Graduation Level
    post_graduation_exam = models.CharField(max_length=200,choices=POST_GRADUATION_EXAM_CHOICES,blank=True, null=True)
    post_graduation_subject = models.CharField(max_length=100, blank=True, null=True)
    post_graduation_university = models.CharField(max_length=100, blank=True, null=True)
    post_graduation_result_type = models.CharField(max_length=100,choices=POST_GRADUATION_RESULT_TYPE_CHOICES, blank=True, null=True)
    post_graduation_result = models.DecimalField(max_digits=4,decimal_places=2,validators=[MinValueValidator(1.00),MaxValueValidator(9.99)], blank=True, null=True)
    post_graduation_passing_year = models.IntegerField(choices=POST_GRADUATION_PASSING_YEAR, blank=True, null=True)
    post_graduation_course_duration = models.CharField(choices=POST_GRADUATION_COURSE_DUARATION,max_length=20, blank=True, null=True)
    create_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True) 

    def _str_(self):
        return f"{self.applicant} - academic"


    @staticmethod
    def get_all_choices():
        """
        To show dynamic data from model to template
        """
        return {
            "ssc_exam_choices": AcademicQualification.SSC_EXAM_CHOICES,
            "ssc_board_choices": AcademicQualification.SSC_BOARD_CHOICES,
            "result_type_choices": AcademicQualification.RESULT_TYPE_CHOICES,
            "ssc_group_choices": AcademicQualification.SSC_GROUP_CHOICES,
            "ssc_passing_year": AcademicQualification.SSC_PASSING_YEAR_CHOICES,
            # HSC
            "hsc_exam_choices": AcademicQualification.HSC_EXAM_CHOICES,
            "hsc_board_choices": AcademicQualification.HSC_BOARD_CHOICES,
            "hsc_result_type_choices": AcademicQualification.HSC_RESULT_TYPE_CHOICES,
            "hsc_group_choices": AcademicQualification.HSC_GROUP_CHOICES,
            "hsc_passing_year_choices": AcademicQualification.HSC_PASSING_YEAR_CHOICES,
            # Graduation
            "graduation_exam_choice": AcademicQualification.GRADUATION_EXAM_CHOICES,
            "graduation_result_type_choice": AcademicQualification.GRADUATION_RESULT_TYPE_CHOICES,
            "graduation_passing_year_choice": AcademicQualification.GRADUATION_PASSING_YEAR_CHOICE,
            "graduation_course_duration_choice": AcademicQualification.GRADUATION_COURSE_DUARATION_CHOICE,
            # Post-Graduation
            "post_graduation_exam_choice": AcademicQualification.POST_GRADUATION_EXAM_CHOICES,
            "post_graduation_result_type_choice": AcademicQualification.POST_GRADUATION_RESULT_TYPE_CHOICES,
            "post_graduation_passing_year_choice": AcademicQualification.POST_GRADUATION_PASSING_YEAR,
            "post_graduation_course_duration_choice": AcademicQualification.POST_GRADUATION_COURSE_DUARATION,
            }

def validate_dimensions(image, width, height):
    w, h = get_image_dimensions(image)
    if w != width or h != height:
        raise ValidationError(f'ছবির আকার {width}x{height} পিক্সেল হতে হবে।')




class Photo(models.Model):
    applicant = models.OneToOneField(
        UserRegistration, on_delete=models.CASCADE,
        related_name="applicant_photo",
        null=True, blank=True
    )
    applicant_image = models.ImageField(upload_to='photos/', default='applicant_img')
    applicant_sig = models.ImageField(upload_to='signatures/', default='applicant_img')
    create_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True) 

    def clean(self):
        super().clean()
        # Image size validation
        w, h = get_image_dimensions(self.applicant_image)
        if w != 300 or h != 300:
            raise ValidationError('Applicant image must be 300x300 pixels.')
        w, h = get_image_dimensions(self.applicant_sig)
        if w != 300 or h != 80:
            raise ValidationError('Applicant signature must be 300x80 pixels.')





class Payment(models.Model):
    BKASH = 'bkash'
    NAGAD = 'nagad'
    METHOD_CHOICES = [
        (BKASH, 'Bkash'),
        (NAGAD, 'Nagad'),
    ]

    applicant = models.OneToOneField(
        UserRegistration, 
        on_delete=models.CASCADE, 
        related_name="payment", 
        limit_choices_to={'role': 'applicant'}
    )
    transaction_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('Paid', 'Paid'), ('Pending', 'Pending')], default='Pending')
    payment_method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    
    def save(self, *args, **kwargs):
        is_new_paid = False

        if self.pk:
            prev_status = Payment.objects.get(pk=self.pk).status
            if prev_status != 'Paid' and self.status == 'Paid':
                is_new_paid = True
        elif self.status == 'Paid':
            is_new_paid = True

        super().save(*args, **kwargs)

        # শর্তগুলো যাচাই
        applicant = self.applicant

        if (
            is_new_paid and
            applicant.role == 'applicant' and
            applicant.intake and
            applicant.roll_number is None
        ):
            try:
                with transaction.atomic():
                    starting_roll = StartingRoll.objects.select_for_update().get(intake=applicant.intake)
                    roll_number = str(starting_roll.starting_number).zfill(6)

                    applicant.roll_number = roll_number
                    applicant.save()

                    starting_roll.starting_number += 1
                    starting_roll.save()
            except StartingRoll.DoesNotExist:
                # intake এর জন্য StartingRoll নেই, কিছুই করো না বা লগ করতে পারো
                pass


class ResultPrepare(models.Model):
    CATEGORY_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]

    applicant = models.OneToOneField(UserRegistration, on_delete=models.CASCADE, related_name="result_prepare")
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)
    mcq_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    job_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    academic_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    


    def calculate_academic_marks(self):
        try:
            aq = self.applicant.academic_qualification
        except AcademicQualification.DoesNotExist:
            return Decimal('0.00')

        # === SSC ===
        ssc = self.get_marks_by_type(
            result=aq.ssc_result,
            result_type=aq.ssc_result_type,
            fixed_class_map={'1st Class': 4.38, '2nd Class': 3.75},
            out_of=5,
            label='SSC'
        )

        # === HSC ===
        hsc = self.get_marks_by_type(
            result=aq.hsc_result,
            result_type=aq.hsc_result_type,
            fixed_class_map={'1st Class': 4.38, '2nd Class': 3.75},
            out_of=5,
            label='HSC'
        )

        # === GRADUATION ===
        grad = self.get_marks_by_type(
            result=aq.graduation_result,
            result_type=aq.graduation_result_type,
            fixed_class_map={'1st Class': 17.5, '2nd Class': 15},
            out_of=20,
            label='Graduation'
        )

        # === POST GRADUATION ===
        post = self.get_marks_by_type(
            result=aq.post_graduation_result,
            result_type=aq.post_graduation_result_type,
            fixed_class_map={'1st Class': 3.5, '2nd Class': 3.0},
            out_of=5,
            label='Post Graduation'
        )

        return ssc + hsc + grad + post

    def get_marks_by_type(self, result, result_type, fixed_class_map, out_of, label=""):
        """
        result: actual numeric GPA or CGPA
        result_type: which type (e.g. "1st Class", "GPA (out of 4)" etc.)
        fixed_class_map: dict mapping fixed class types to values (e.g. 1st Class = 4.38)
        out_of: the value to scale to (e.g. 5, 20 etc.)
        """
        if result_type in fixed_class_map:
            return Decimal(fixed_class_map[result_type])

        # If GPA
        if result_type == "GPA (out of 4)":
            scale = 4
        elif result_type == "GPA (out of 5)":
            scale = 5
        else:
            return Decimal('0.00')

        if result is None:
            return Decimal('0.00')

        try:
            return (Decimal(result) / Decimal(scale)) * Decimal(out_of)
        except (ArithmeticError, TypeError, ValueError):
            return Decimal('0.00')

    def save(self, *args, **kwargs):
        self.academic_marks = self.calculate_academic_marks()
        self.total_marks = Decimal(self.mcq_marks) + Decimal(self.job_marks) + self.academic_marks
        super().save(*args, **kwargs)





# 




class MainGallery(models.Model):
    background_img = models.ImageField(upload_to='background_img/', blank=True, null=True)
    heading = models.CharField(max_length=35, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# সিগন্যাল: ডিলেট করার পর ফাইলও ডিলেট হবে
@receiver(post_delete, sender=MainGallery)
def delete_image_file(sender, instance, **kwargs):
    if instance.background_img:
        if os.path.isfile(instance.background_img.path):
            os.remove(instance.background_img.path)


class HomeContent(models.Model):  
    department_description = models.TextField(blank=True, null=True)
    department_img = models.ImageField(upload_to='department_img/', blank=True, null=True)

    chairman = models.ForeignKey(
        UserRegistration,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='chairman',
        limit_choices_to={'role': 'teacher'}
    )
    chairman_image = models.ImageField(upload_to='chairman_img/', blank=True, null=True)
    chairman_message = models.TextField(blank=True, null=True)

    co_ordinator = models.ForeignKey(
        UserRegistration,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='co_ordinator',
        limit_choices_to={'role': 'teacher'}
    )
    co_ordinato_image = models.ImageField(upload_to='coordinator_img/', blank=True, null=True)
    co_ordinator_message = models.TextField(blank=True, null=True)
    founded = models.IntegerField(blank=True, null=True)
    faculties = models.IntegerField(blank=True, null=True)
    students = models.IntegerField(blank=True, null=True)
    passed_students = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# ✅ সিগন্যাল: HomeContent মডেল ডিলিট হলে ফাইলও মুছে যাবে
@receiver(post_delete, sender=HomeContent)
def delete_department_img(sender, instance, **kwargs):
    if instance.department_img:
        if os.path.isfile(instance.department_img.path):
            os.remove(instance.department_img.path)


