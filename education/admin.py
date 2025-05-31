
from django.contrib import admin
from .models import *

from django.utils.html import format_html



@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('batch_name', 'intake', 'position_no', 'created')
    search_fields = ('batch_name', 'intake')
    ordering = ('position_no',)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('semester_name', 'position_no', 'created')
    search_fields = ('semester_name',)
    ordering = ('position_no',)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('section_name', 'position_no', 'created')
    search_fields = ('section_name',)
    ordering = ('position_no',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'course_name', 'credit', 'position_no', 'created')
    search_fields = ('course_code', 'course_name')
    ordering = ('position_no',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('batch', 'semester', 'section','course', 'teachers_list', 'students_list', 'create_at')
    list_filter = ('batch', 'semester', 'section', 'course')
    search_fields = ('course__course_code', 'batch__batch_name', 'semester__semester_name', 'section__section_name')
    filter_horizontal = ('teachers', 'students')  # For ManyToManyFields
    autocomplete_fields = ('batch', 'semester', 'section', 'course')  # Optional if ForeignKeys are large
    date_hierarchy = 'create_at'
    ordering = ('-create_at',)
    
    def teachers_list(self, obj):
        return format_html(
            '<br>'.join([teacher.full_name for teacher in obj.teachers.all()])
        ) if obj.teachers.exists() else "No Teachers"
    teachers_list.short_description = 'Teachers'

    def students_list(self, obj):
        return format_html(
            '<br>'.join([student.full_name for student in obj.students.all()])
        ) if obj.students.exists() else "No Students"
    students_list.short_description = 'Students'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('batch', 'semester', 'section', 'course').prefetch_related('teachers', 'students')

