from django import forms
from django.core.exceptions import ValidationError
from .models import *

class EnrollmentEditForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['batch', 'semester', 'section', 'course', 'teachers', 'students']
        widgets = {
            'batch': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'teachers': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'students': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        batch = cleaned_data.get('batch')
        semester = cleaned_data.get('semester')
        section = cleaned_data.get('section')
        course = cleaned_data.get('course')

        if batch and semester and course:
            existing = Enrollment.objects.filter(
                batch=batch,
                semester=semester,
                section=section,
                course=course
            )

            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise ValidationError("⛔ এই Batch, Semester, Section এবং Course কম্বিনেশনে ইতিমধ্যে একটি এন্ট্রি আছে।")

        return cleaned_data
