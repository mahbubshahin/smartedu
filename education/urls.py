
from django.urls import path
from.views import *


urlpatterns = [
    # manager 
    path('enrolled_student_list/', enrolled_student_list, name='enrolled_student_list'),
    path('enroll/', student_enroll, name='student_enroll'),   
    path('enrollment_summary/', enrollment_summary, name='enrollment_summary'),
    path('student-courses/<int:student_id>/', student_courses, name='student_courses'),

    # Teacher
    path('teacher_wise_student', teacher_wise_student, name='teacher_wise_student'),

]


