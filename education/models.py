
from django.db import models

from accounts.models import UserRegistration
from django.utils import timezone

import json
from django.db import models
from django.core.exceptions import ValidationError


# Create your models here.



class Batch(models.Model):
    batch_name = models.CharField(max_length=50, unique=True, blank=False, null=False)
    intake = models.CharField(max_length=30, unique=True, blank=False, null=False,)
    position_no = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position_no']

    def __str__(self):
        return self.batch_name 
    
    
class Semester(models.Model):
    semester_name = models.CharField(max_length=100, blank=False, null=False)
    position_no = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position_no']

    def __str__(self):
        return self.semester_name

class Section(models.Model):
    section_name = models.CharField(max_length=20, unique=True, blank=False, null=False)
    position_no = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position_no']

    def __str__(self):
        return f"Section {self.section_name}"


    
class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True, blank=False, null=False)
    course_name = models.CharField(max_length=255, blank=False, null=False)
    credit = models.DecimalField(max_digits=4, decimal_places=2, blank=False, null=False)
    position_no = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position_no']

    def __str__(self):
        return self.course_code
    


class Enrollment(models.Model):
    teachers = models.ManyToManyField(UserRegistration, limit_choices_to={'role': UserRegistration.TEACHER}, related_name='teacher_assignments')
    students = models.ManyToManyField(UserRegistration, limit_choices_to={'role': UserRegistration.STUDENT}, related_name='student_enrollments')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='batch_enroll')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='sem_enroll')
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='sec_enroll')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_enroll')
    create_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('batch', 'semester', 'section', 'course')
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        ordering = ['-create_at']

    def __str__(self):
        section_display = self.section.section_name if self.section else "No Section"
        return f"{self.course} | {self.batch} | {self.semester} | {section_display}"



# 



class GradeScale(models.Model):
    min_marks = models.DecimalField(max_digits=4, decimal_places=2)
    max_marks = models.DecimalField(max_digits=4, decimal_places=2)
    letter_grade = models.CharField(max_length=5)
    grade_point = models.DecimalField(max_digits=4, decimal_places=2)

    def _str_(self):
        return f"{self.letter_grade} ({self.min_marks}-{self.max_marks})"
    


class MarkInputPermission(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        current_time = timezone.now()
        return self.active and self.start_date <= current_time <= self.end_date



class MarkEntry(models.Model):
    student = models.ForeignKey(UserRegistration, on_delete=models.SET_NULL, limit_choices_to={'role': UserRegistration.STUDENT}, related_name='student_marks',  null=True, blank=True)

    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    mid_marks = models.TextField(blank=True, default='{}')   
    final_marks = models.TextField(blank=True, default='{}')  
    
    total_mid = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    total_final = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    grand_total = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    letter_grade = models.CharField(max_length=5, blank=True, null=True)
    grade_point = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    teacher = models.ForeignKey(UserRegistration, on_delete=models.SET_NULL, limit_choices_to={'role': UserRegistration.TEACHER}, related_name='given_marks', blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def parse_marks(self, marks_field):
        try:
            return json.loads(marks_field)
        except json.JSONDecodeError:
            return {}

    def calculate_total(self, marks_dict):
        if "Absent" in marks_dict and marks_dict["Absent"] is True:
            return 0
        return sum(marks_dict.values())

    def clean(self):
        mid_dict = self.parse_marks(self.mid_marks)
        final_dict = self.parse_marks(self.final_marks)

        total_mid = self.calculate_total(mid_dict)
        total_final = self.calculate_total(final_dict)

        if total_mid and "Absent" not in final_dict and not final_dict:
            # Allow midterm only for now
            return
        elif total_mid == 0 or (total_final == 0 and "Absent" not in final_dict):
            raise ValidationError("Mid or Final marks missing or incomplete.")

        if (total_mid + total_final) > 100:
            raise ValidationError("Total marks cannot exceed 100.")

    def save(self, *args, **kwargs):
        mid_dict = self.parse_marks(self.mid_marks)
        final_dict = self.parse_marks(self.final_marks)

        self.total_mid = self.calculate_total(mid_dict)
        self.total_final = self.calculate_total(final_dict)
        self.grand_total = self.total_mid + self.total_final

        if self.total_mid == 0 or ("Absent" in final_dict and final_dict["Absent"] is True):
            self.letter_grade = 'Absent'
            self.grade_point = 0.00
        elif self.grand_total:
            grade_scale = GradeScale.objects.filter(
                min_marks__lte=self.grand_total,
                max_marks__gte=self.grand_total
            ).first()
            if grade_scale:
                self.letter_grade = grade_scale.letter_grade
                self.grade_point = grade_scale.grade_point

        super().save(*args, **kwargs)

    def get_mid_marks_dict(self):
        return self.parse_marks(self.mid_marks)

    def get_final_marks_dict(self):
        return self.parse_marks(self.final_marks)

    def __str__(self):
        return f"{self.student} - {self.course.course_code}"


