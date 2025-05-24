# urls.py

from django.urls import path
from .views import *



urlpatterns = [
    path('', home, name='home'),
    path('applicant/', applicant_register, name='applicant_register'),
    path('common-user/', coustom_user_registration, name='coustom_user_registration'),
   
    # 
    path('login/', login, name='login'),
    path('logout/', applicant_logout, name='applicant_logout'),
    path('forgot-password/', applicant_forgot_password, name='applicant_forgot_password'),
    path('verify-otp/', applicant_verify_otp, name='applicant_verify_otp'),
    path('reset-password/', reset_password, name='reset_password'),
    path('change-password/', change_password, name='change_password'),

    # 
    path('teacher_dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('manager/', manager_dashboard, name='manager_dashboard'),
    path('student/', student_dashboard, name='student_dashboard'),
    path('accountant/', accountant_dashboard, name='accountant_dashboard'),
    path('dashboard/', applicant_dashboard, name='applicant_dashboard'),
    



]