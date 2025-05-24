# urls.py

from django.urls import path
from .views import *



urlpatterns = [

    path('notice/', Admission_Notice, name='Admission_Notice'),
    path('syllabus/', syllabus_info, name='syllabus_info'),
    path('procedure/', admission_procedure, name='admission_procedure'),
    # 
    path("personal-info/", personal_info, name="personal_info"),
    path("academic_qualification/", academic_qualification, name="academic_qualification"),
    path("review/", application_review, name="application_review"),
    path('payment/', payment,name='payment'),
    path('admit-card/', admit_card_pdf, name='admit_card_pdf'),
    path('resize/', image_resize, name='image_resize'),


    # 

    path('status/',applicant_status, name='applicant_status'),
    path('applicant_list', applicant_list, name='applicant_list'),
    path('export/', export_applicants_excel, name='export_applicants_excel'),
    path('applicant/<int:applicant_id>/', applicant_detail, name='applicant_detail'),
    path('send-sms/', send_message_to_applicants, name='send_message_to_applicants'),
    path('send-email/', send_email_to_applicants, name='send_email_to_applicants'),
    path('written_att/', written_attendance_pdf, name='written_attendance_pdf'),
    path('viv_att/', viva_attendance_pdf, name='viva_attendance_pdf'),
    path('result/', result_prepare, name='result_prepare'),


    

]