# 🖼 Rendering & templating (টেমপ্লেট রেন্ডার করতে বা দেখাতে)
from django.shortcuts import render, redirect, get_object_or_404  # পেইজ রেন্ডার বা রিডাইরেক্ট করতে

# 📤 HTTP responses (রেসপন্স পাঠাতে)
from django.http import HttpResponse, FileResponse  # HTML বা ফাইল ডাউনলোড রেসপন্স পাঠাতে

# ⚙️ Django core utilities and settings (কনফিগারেশন ও ইউটিলিটির জন্য)
from django.conf import settings  # Django প্রজেক্ট সেটিংস অ্যাক্সেস করার জন্য
from django.urls import reverse  # ভিউ-এর নাম দিয়ে URL জেনারেট করতে
from django.utils import timezone  # টাইমজোন অনুযায়ী সময় ব্যবহারে
from django.utils.timezone import now  # বর্তমান সময় নেয়ার জন্য
from django.core.exceptions import PermissionDenied  # পারমিশন না থাকলে এরর দিতে

from django.utils.timezone import now
from django.db.models import Max
# 🔐 Authentication (লগইন, পারমিশন চেক করতে)
from django.contrib.auth import authenticate, login as auth_login, logout, update_session_auth_hash  # ইউজার অথেন্টিকেশন
from django.contrib.auth.decorators import login_required  # ভিউতে লগইন বাধ্যতামূলক করতে

# 📬 Email utilities (ইমেইল পাঠাতে)
from django.core.mail import send_mail  # সাধারণ ইমেইল পাঠাতে
from django.core.mail import EmailMessage  # এটাচমেন্টসহ ইমেইল পাঠাতে

# 🧠 ORM & Query-related imports (ডাটাবেজ থেকে কুয়েরি চালাতে)
from django.db import IntegrityError  # ডুপ্লিকেট বা ডাটাবেজ এরর ধরতে
from django.db.models import Q, Min, Max  # কন্ডিশনাল কুয়েরির জন্য

# 🧾 PDF generation using xhtml2pdf (PDF তৈরি করতে)
from xhtml2pdf import pisa  # HTML থেকে PDF তৈরি করতে ব্যবহৃত লাইব্রেরি

# 🧰 Python built-in modules (জেনারেল ইউটিলিটি কাজের জন্য)
import random  # র‍্যান্ডম সংখ্যা বা স্ট্রিং তৈরি করতে
import string  # স্ট্রিং জেনারেট করতে
import io  # ইন-মেমোরি ফাইল হ্যান্ডল করতে
import os  # ফাইল সিস্টেমের সাথে কাজ করতে
import base64  # বেস64 ফরম্যাটে ফাইল বা ডেটা রূপান্তর করতে

# 🏠 Local app imports (লোকাল মডেল ইম্পোর্ট)
from .models import *  # লোকাল অ্যাপের মডেলস ইউজ করতে
from admission.models import *  # অ্যাডমিশন সম্পর্কিত মডেলস
from education.models import *

from django.contrib import messages


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, logout
from django.shortcuts import render, redirect



import random
import string
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.db import IntegrityError
from django.conf import settings



from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from django.http import JsonResponse
import random



# Create your views here.


def home(request):
    main_gallery = MainGallery.objects.all().order_by('position') 
    home_content = HomeContent.objects.last()

    # যারা শিক্ষক এবং position_no আছে, তাদের আগে আনবে
    teachers_with_position = UserRegistration.objects.filter(
        role=UserRegistration.TEACHER,
        position_no__isnull=False
    ).order_by('position_no')

    # যাদের position_no নেই, তাদের পরে আনবে
    teachers_without_position = UserRegistration.objects.filter(
        role=UserRegistration.TEACHER,
        position_no__isnull=True
    )

    # দুই queryset মিলিয়ে পূর্ণ শিক্ষক তালিকা তৈরি
    teachers = list(teachers_with_position) + list(teachers_without_position)

    courses = Course.objects.all().order_by('position_no') 

    context = {
        'main_gallery': main_gallery,
        'home_content': home_content,
        'teachers': teachers,
        'courses': courses
    }

    return render(request, 'accounts/home.html', context)






# # ✅ CAPTCHA জেনারেটর ফাংশন (utils.py বাদ দিয়ে ভিউয়ের ভেতরে)
def generate_registration_captcha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))



def applicant_register(request):
    now = timezone.now()

    # সব একটিভ ইনটেক
    active_intakes = Intake.objects.filter(is_open=True).order_by('-start_date')

    # যেগুলো বর্তমানে চলমান
    running_intakes = active_intakes.filter(start_date__lte=now, end_date__gte=now)

    intake = None
    context = {}

    if running_intakes.exists():
        # সর্বশেষ শুরু হওয়া ইনটেক
        intake = running_intakes.first()
        context['intake_name'] = intake.intake_name
    elif active_intakes.exists():
        # ভবিষ্যতে শুরু হবে এমন ইনটেক
        upcoming_intake = active_intakes.first()
        context['registration_upcoming'] = True
        context['intake_name'] = upcoming_intake.intake_name
        context['start_date'] = upcoming_intake.start_date
        return render(request, 'accounts/applicant_registration.html', context)
    else:
        # কোনো একটিভ ইনটেক নেই
        context['registration_closed'] = True
        return render(request, 'accounts/applicant_registration.html', context)

    # রেজিস্ট্রেশন ফর্ম হ্যান্ডলিং
    if request.method == "GET" and request.GET.get("refresh_captcha") == "1":
        new_captcha = generate_registration_captcha()
        request.session['registration_captcha'] = new_captcha
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'new_captcha': new_captcha})
        return redirect('applicant_register')

    if request.method == "GET":
        request.session['registration_captcha'] = generate_registration_captcha()

    if request.method == "POST":
        otp = request.POST.get("otp")
        if otp:
            temp_data = request.session.get('temp_data')
            if not temp_data:
                messages.error(request, "Session expired. Please register again.")
                return redirect('applicant_register')

            otp_code = temp_data.get('otp_code')
            otp_created_at = timezone.datetime.fromisoformat(temp_data['otp_created_at'])

            if otp != otp_code or timezone.now() > otp_created_at + timezone.timedelta(minutes=10):
                messages.error(request, "Invalid or expired OTP.")
                return render(request, 'accounts/applicant_registration.html', {
                    'submitted': True,
                    'email': temp_data['email'],
                })

            user = UserRegistration(
                full_name=temp_data['full_name'],
                username=temp_data['username'],
                email=temp_data['email'],
                mobile_number=temp_data['mobile_number'],
                role='applicant',
                is_email_verified=True,
                intake=intake
            )
            user.set_password(temp_data['password'])

            try:
                user.save()
                del request.session['temp_data']
                messages.success(request, "Your account has been successfully created.")
                return redirect('login')
            except IntegrityError:
                messages.error(request, "A user with this email or mobile number already exists.")
                return render(request, 'accounts/applicant_registration.html', {
                    'submitted': False,
                    'captcha': generate_registration_captcha(),
                })

        # CAPTCHA যাচাইকরণ
        input_captcha = request.POST.get("captcha")
        session_captcha = request.session.pop('registration_captcha', None)

        if not input_captcha or input_captcha.upper() != session_captcha:
            new_captcha = generate_registration_captcha()
            request.session['registration_captcha'] = new_captcha
            messages.error(request, "Invalid CAPTCHA.")
            return render(request, 'accounts/applicant_registration.html', {
                'submitted': False,
                'captcha': new_captcha,
            })

        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        mobile_number = request.POST.get("mobile_number")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            new_captcha = generate_registration_captcha()
            request.session['registration_captcha'] = new_captcha
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/applicant_registration.html', {
                'submitted': False,
                'captcha': new_captcha,
            })

        otp_code = str(random.randint(100000, 999999))
        request.session['temp_data'] = {
            'full_name': full_name,
            'username': username,
            'email': email,
            'mobile_number': mobile_number,
            'password': password,
            'otp_code': otp_code,
            'otp_created_at': timezone.now().isoformat()
        }

        send_mail(
            subject="Your OTP Code",
            message=f"Your OTP code is: {otp_code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return render(request, 'accounts/applicant_registration.html', {
            'submitted': True,
            'email': email,
        })

    context['captcha'] = request.session.get('registration_captcha')
    context['intake_name'] = intake.intake_name
    return render(request, 'accounts/applicant_registration.html', context)


def coustom_user_registration(request):
    if not request.user.is_authenticated or request.user.role != UserRegistration.MANAGER:
        messages.warning(request, "You are not authorized to access this page.")
        return redirect("home")

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        mobile_number = request.POST.get("mobile_number")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        selected_role = request.POST.get("user_type")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
        elif UserRegistration.objects.filter(email=email).exists():
            messages.error(request, "A user with this email already exists.")
        elif UserRegistration.objects.filter(username=username).exists():
            messages.error(request, "A user with this username already exists.")
        elif UserRegistration.objects.filter(mobile_number=mobile_number).exists():
            messages.error(request, "A user with this mobile number already exists.")
        else:
            try:
                user = UserRegistration(
                    full_name=full_name,
                    username=username,
                    email=email,
                    mobile_number=mobile_number,
                    role=selected_role,
                    is_email_verified=True,
                )
                user.set_password(password)
                user.save()
                messages.success(request, f"{selected_role.capitalize()} account created successfully.")
                return redirect("coustom_user_registration")  # Or to another page
            except IntegrityError:
                messages.error(request, "A user with this information already exists.")

    context = {
        "user_type": UserRegistration.ROLE_CHOICES,
    }
    return render(request, "accounts/coustom_user_registration.html", context)





def login(request):
    # আগেই লগইন করা থাকলে পূর্বের পেজে বা home-এ পাঠাও
    if request.user.is_authenticated:
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('home')

    next_url = request.GET.get('next')  # URL এর ?next=/xyz থেকে আসা পাথ

    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        user = authenticate(request, username=username_or_email, password=password)
        if user is not None:
            # ✅ Applicant হলে প্রথমে intake চেক করো
            if user.role == UserRegistration.APPLICANT:
                active_intake = Intake.objects.filter(
                    is_open=True,
                 
                )

                if not active_intake.exists():
                    messages.warning(request, "Registration period is closed. You cannot login as Applicant now.")
                    return redirect('login')  # আবার লগইন পেইজে পাঠানো

            auth_login(request, user)
            messages.success(request, "You are successfully login")

            # ✅ যদি next URL থাকে এবং নিরাপদ হয়
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)

            # ✅ role অনুযায়ী রিডাইরেক্ট
            if user.role == UserRegistration.TEACHER:
                return redirect('teacher_dashboard')
            elif user.role == UserRegistration.MANAGER:
                return redirect('manager_dashboard')
            elif user.role == UserRegistration.STUDENT:
                return redirect('student_dashboard')
            elif user.role == UserRegistration.ACCOUNTANT:
                return redirect('student_dashboard')
            elif user.role == UserRegistration.APPLICANT:
                return redirect('applicant_dashboard')
            else:
                return redirect('home') 

        else:
            messages.error(request, "Invalid credentials. Please try again.")

    return render(request, 'accounts/login.html')



def applicant_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')



def applicant_forgot_password(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')  
        try:
            user = UserRegistration.objects.filter(models.Q(email=username_or_email) | models.Q(username=username_or_email)).first()
            if not user:
                messages.error(request, "No account found with this email or username.")
                return redirect('applicant_forgot_password')

            otp_code = str(random.randint(100000, 999999))
            request.session['reset_otp'] = otp_code
            request.session['user_email'] = user.email
            request.session['otp_created_at'] = timezone.now().isoformat()

            # ইমেইল পাঠানো
            reset_link = request.build_absolute_uri('/reset-password/')
            send_mail(
                subject="Password Reset Request",
                message=f"Your OTP code is {otp_code}. Alternatively, click this link to reset your password: {reset_link}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
            )

            messages.success(request, f"OTP and reset link have been sent to your email: {user.email}")
            return redirect('applicant_verify_otp')
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")
            print(e)
    return render(request, 'accounts/forgot_password.html')



def applicant_verify_otp(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        stored_otp = request.session.get('reset_otp')
        otp_created_at = timezone.datetime.fromisoformat(request.session.get('otp_created_at'))

        if not stored_otp or timezone.now() > otp_created_at + timezone.timedelta(minutes=10):
            messages.error(request, "OTP expired. Please request a new one.")
            return redirect('applicant_forgot_password')

        if otp_entered != stored_otp:
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'accounts/verify_otp.html')

        messages.success(request, "OTP verified successfully. Please reset your password.")
        return redirect('reset_password')
    return render(request, 'accounts/verify_otp.html')


def reset_password(request):
    user_email = request.session.get('user_email')

    if not user_email:
        messages.error(request, "Session expired. Please request password reset again.")
        return redirect('applicant_forgot_password')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('reset_password')

        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('reset_password')

        # পাসওয়ার্ড রিসেট করা হচ্ছে
        user = UserRegistration.objects.get(email=user_email)
        user.set_password(new_password)
        user.save()

        messages.success(request, "Your password has been reset successfully.")
        del request.session['user_email']
        del request.session['reset_otp']
        del request.session['otp_created_at']
        return redirect('login')
    return render(request, 'accounts/reset_password.html')



# @login_required
# def change_password(request):
#     if request.method == 'POST':
#         current_password = request.POST.get('current_password')
#         new_password = request.POST.get('new_password')
#         confirm_password = request.POST.get('confirm_password')

#         if not request.user.check_password(current_password):
#             messages.error(request, 'Your current password is incorrect.')
#         elif new_password != confirm_password:
#             messages.error(request, 'New passwords do not match.')
#         elif len(new_password) < 8:
#             messages.error(request, 'New password must be at least 8 characters long.')
#         else:
#             request.user.set_password(new_password)
#             request.user.save()
#             update_session_auth_hash(request, request.user)
#             messages.success(request, 'Your password has been changed successfully.')
#             logout(request)
#             return redirect('login')

#     context = {
#         'active_password_change': True  
#     }

#     # টেমপ্লেট নির্বাচন
#     if request.user.role == request.user.MANAGER:
#         template = 'accounts/manager_dashboard.html'
#     else:
#         template = 'accounts/applicant_dashboard.html'

#     return render(request, template, context)



from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, logout
from django.shortcuts import render, redirect

@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request, 'Your current password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password) < 8:
            messages.error(request, 'New password must be at least 8 characters long.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Your password has been changed successfully.')
            logout(request)
            return redirect('login')

    context = {
        'active_password_change': True
    }

    # প্রতিটি রোল অনুযায়ী টেমপ্লেট নির্বাচন
    if request.user.role == request.user.MANAGER:
        template = 'accounts/manager_dashboard.html'
    elif request.user.role == request.user.APPLICANT:
        template = 'accounts/applicant_dashboard.html'
    elif request.user.role == request.user.TEACHER:
        template = 'accounts/teacher_dashboard.html'
    elif request.user.role == request.user.STUDENT:
        template = 'accounts/student_dashboard.html'
    else: 
        template = 'accounts/accountant_dashboard.html'

    return render(request, template, context)


# ----------------------------


@login_required
def teacher_dashboard(request):
    if request.user.role != UserRegistration.TEACHER:
        raise PermissionDenied("You are not authorized to access this page.")

    context = {
        'teacher': request.user,
    }
    return render(request, 'accounts/teacher_dashboard.html', context)


@login_required
def manager_dashboard(request):
    if request.user.role != UserRegistration.MANAGER:
        raise PermissionDenied("You are not authorized to access this page.")

    context = {
        'manager': request.user,
    }
    return render(request, 'accounts/manager_dashboard.html', context)


@login_required
def student_dashboard(request):
    if request.user.role != UserRegistration.STUDENT:
        raise PermissionDenied("You are not authorized to access this page.")

    context = {
        'student': request.user,
    }
    return render(request, 'accounts/student_dashboard.html', context)



@login_required
def accountant_dashboard(request):
    if request.user.role != UserRegistration.ACCOUNTANT:
        raise PermissionDenied("You are not authorized to access this page.")

    context = {
        'accountant': request.user,
    }
    return render(request, 'accounts/accountant_dashboard.html', context)





@login_required
def applicant_dashboard(request):
    if request.user.role != request.user.APPLICANT:
        raise PermissionDenied("You are not authorized to access this page.")

    applicant = request.user

    # Check if profile is completed
    profile_complete = (
        PersonalInformation.objects.filter(applicant=applicant).exists() and
        AcademicQualification.objects.filter(applicant=applicant).exists() and
        Photo.objects.filter(applicant=applicant).exists()
    )

    # Check if payment is completed
    payment = getattr(applicant, 'payment', None)
    payment_status = payment.status if payment else "Pending"
    payment_complete = payment_status == "Paid"

    # Get the intake name
    intake_name = applicant.intake.intake_name if applicant.intake else "Not assigned"

    # Get latest updated_at from relevant models (excluding None)
    update_times = []

    pi = PersonalInformation.objects.filter(applicant=applicant).aggregate(Max('updated_at'))['updated_at__max']
    if pi:
        update_times.append(pi)

    aq = AcademicQualification.objects.filter(applicant=applicant).aggregate(Max('updated_at'))['updated_at__max']
    if aq:
        update_times.append(aq)

    ph = Photo.objects.filter(applicant=applicant).aggregate(Max('updated_at'))['updated_at__max']
    if ph:
        update_times.append(ph)

    pm = Payment.objects.filter(applicant=applicant).aggregate(Max('updated_at'))['updated_at__max']
    if pm:
        update_times.append(pm)

    latest_update = max(update_times) if update_times else None

    context = {
        'applicant': applicant,
        'profile_complete': profile_complete,
        'payment_complete': payment_complete,
        'intake_name': intake_name,
        'latest_update': latest_update,
    }

    return render(request, 'accounts/applicant_dashboard.html', context)
