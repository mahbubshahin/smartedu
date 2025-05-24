
# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.core.paginator import Paginator
from collections import OrderedDict
import openpyxl
from django.db import IntegrityError

from django.utils.http import url_has_allowed_host_and_scheme  # সেফ URL যাচাই করতে



# Models
from .models import *

from .forms import *
from django.db.models import Q

# Modelformset Factory
from django.forms import modelformset_factory


from collections import OrderedDict
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse
import openpyxl



def enrolled_student_list(request):
    if not hasattr(request.user, 'role') or request.user.role != UserRegistration.MANAGER:
        messages.warning(request, "⛔ You are not authorized to access this page.")
        return redirect('home')

    batches = Batch.objects.all()
    selected_batch_id = request.GET.get('batch')
    selected_semester_id = request.GET.get('semester')
    selected_section_id = request.GET.get('section')
    selected_course_id = request.GET.get('course')
    search_roll = request.GET.get('roll')

    semesters = Semester.objects.none()
    sections = Section.objects.none()
    courses = Course.objects.none()

    enrollments = Enrollment.objects.prefetch_related('students', 'teachers').all()

    if selected_batch_id:
        enrollments = enrollments.filter(batch_id=selected_batch_id)
        semesters = Semester.objects.filter(id__in=enrollments.values_list('semester_id', flat=True).distinct())

    if selected_semester_id:
        enrollments = enrollments.filter(semester_id=selected_semester_id)
        sections = Section.objects.filter(id__in=enrollments.values_list('section_id', flat=True).distinct())
        courses = Course.objects.filter(id__in=enrollments.values_list('course_id', flat=True).distinct())

    if selected_section_id:
        if selected_section_id == "none":
            enrollments = enrollments.filter(section__isnull=True)
        elif selected_section_id.isdigit():
            enrollments = enrollments.filter(section_id=selected_section_id)

    if selected_course_id:
        enrollments = enrollments.filter(course_id=selected_course_id)

    if search_roll:
        enrollments = enrollments.filter(
            students__roll_number__icontains=search_roll
        ).distinct()

    # Excel Export
    if 'download' in request.GET:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Enrolled Students"

        ws.append(["Roll Number", "Name", "Email", "Phone", "Batch", "Semester", "Section", "Course", "Teachers"])

        for e in enrollments:
            for student in e.students.all():
                teacher_names = ", ".join([t.full_name for t in e.teachers.all()])
                ws.append([
                    student.roll_number,
                    student.full_name,
                    student.email,
                    student.mobile_number,
                    e.batch.batch_name if e.batch else '',
                    e.semester.semester_name if e.semester else '',
                    e.section.section_name if e.section else 'None',
                    e.course.course_code if e.course else '',
                    teacher_names
                ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="enrolled_students.xlsx"'
        wb.save(response)
        return response

    # Unique students (flatten ManyToMany)
    students_set = OrderedDict()
    for e in enrollments.order_by('-id'):
        for s in e.students.all():
            students_set[s.id] = s
    students_list = list(students_set.values())

    paginator = Paginator(students_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Fetch Teachers (for selected filters)
    teachers_set = set()
    if selected_batch_id and selected_semester_id and selected_course_id:
        enrollments_filtered = enrollments.filter(
            batch_id=selected_batch_id,
            semester_id=selected_semester_id,
            course_id=selected_course_id
        )
        teachers_set = set(
            t.id for e in enrollments_filtered for t in e.teachers.all()
        )

    teachers = UserRegistration.objects.filter(id__in=teachers_set, role=UserRegistration.TEACHER)

    context = {
        'batches': batches,
        'semesters': semesters,
        'sections': sections,
        'courses': courses,
        'students': page_obj,
        'page_obj': page_obj,
        'selected_batch_id': selected_batch_id,
        'selected_semester_id': selected_semester_id,
        'selected_section_id': selected_section_id,
        'selected_course_id': selected_course_id,
        'search_roll': search_roll,
        'teachers': teachers,  
    }

    return render(request, 'education/enrolled_student_list.html', context)


def student_enroll(request):
    if not hasattr(request.user, 'role') or request.user.role != UserRegistration.MANAGER:
        messages.warning(request, "⛔ You are not authorized to access this page.")
        return redirect('home')

    # সব ব্যাচ, সেমিস্টার, সেকশন ও কোর্স আনা হচ্ছে
    batches = Batch.objects.all()
    semesters = Semester.objects.all()
    sections = Section.objects.all()
    courses = Course.objects.all()

    # সব স্টুডেন্ট এবং টিচার আনা হচ্ছে
    all_students = UserRegistration.objects.filter(role=UserRegistration.STUDENT).order_by('roll_number')
    all_teachers = UserRegistration.objects.filter(role=UserRegistration.TEACHER)

    # ইউজার কীভাবে শিক্ষার্থী সিলেক্ট করতে চায় সেটি জানা হচ্ছে
    selection_type = request.GET.get('select_type', 'all')
    search_roll = request.GET.get('roll_search', '')
    batch_filter = request.GET.get('batch_filter', '')
    is_new_assign_mode = not batch_filter  # নতুন এস্যাইনমেন্ট মোড বোঝানো হচ্ছে

    # সেশনে পূর্বে সিলেক্ট করা শিক্ষার্থীদের আইডি না থাকলে ফাঁকা লিস্ট সেট করা হচ্ছে
    if 'selected_ids' not in request.session:
        request.session['selected_ids'] = []
    selected_ids = request.session['selected_ids']

    # যদি রোল নাম্বার দিয়ে সার্চ করা হয়
    if search_roll:
        students = all_students.filter(roll_number__icontains=search_roll)
    else:
        students = all_students
        if batch_filter:
            # নির্দিষ্ট ব্যাচের ইনরোল্ড শিক্ষার্থীরা দেখানো হচ্ছে
            students = students.filter(id__in=Enrollment.objects.filter(batch_id=batch_filter).values_list('students__id', flat=True))
        else:
            # ইতোমধ্যে ইনরোল্ড শিক্ষার্থীদের বাদ দিয়ে নতুন শিক্ষার্থীদের তালিকা দেখানো হচ্ছে
            enrolled_student_ids = Enrollment.objects.values_list('students__id', flat=True).distinct()
            students = students.exclude(id__in=enrolled_student_ids)

        # রোল অনুযায়ী ফিল্টার করার ফাংশন
        def filter_students_by_select_type(student_queryset, selection_type):
            if selection_type == 'even':
                return [s for s in student_queryset if s.roll_number and s.roll_number.isdigit() and int(s.roll_number) % 2 == 0]
            elif selection_type == 'odd':
                return [s for s in student_queryset if s.roll_number and s.roll_number.isdigit() and int(s.roll_number) % 2 != 0]
            elif selection_type == 'part1':
                return [s for s in student_queryset if s.roll_number and s.roll_number.isdigit() and (int(s.roll_number) - 3) % 3 == 0]
            elif selection_type == 'part2':
                return [s for s in student_queryset if s.roll_number and s.roll_number.isdigit() and (int(s.roll_number) - 1) % 3 == 0]
            elif selection_type == 'part3':
                return [s for s in student_queryset if s.roll_number and s.roll_number.isdigit() and (int(s.roll_number) - 2) % 3 == 0]
            return student_queryset

        students = filter_students_by_select_type(students, selection_type)

    # পোস্ট মেথডে যদি টিচার সিলেক্ট করা হয়
    selected_teacher_ids = request.POST.getlist('teachers') if request.method == 'POST' else []

    # যদি POST রিকোয়েস্ট হয় (ডেটা সাবমিট করা হয়ে থাকে)
    if request.method == 'POST':
        removed_ids = request.POST.getlist('removed_ids')
        if removed_ids:
            # আগে সিলেক্ট করা তালিকা থেকে যাদের বাদ দেয়া হয়েছে তা রিমুভ করা হচ্ছে
            selected_ids = [sid for sid in selected_ids if sid not in removed_ids]
            request.session['selected_ids'] = selected_ids

        if 'save_selection' in request.POST:
            # শিক্ষার্থীদের সিলেকশন সেভ করা হচ্ছে
            new_ids = request.POST.getlist('students')
            selected_ids = list(set(selected_ids + new_ids))
            request.session['selected_ids'] = selected_ids
            messages.success(request, "✅ Selection saved.")
            return redirect('student_enroll')

        elif 'final_submit' in request.POST:
            # ফাইনাল সাবমিশনের সময় প্রয়োজনীয় ফিল্ডগুলো সংগ্রহ
            selected_batch_id = request.POST.get('batch')
            selected_semester_id = request.POST.get('semester')
            selected_section_id = request.POST.get('section') or None
            selected_course_id = request.POST.get('course')

            # যদি কোনো ফিল্ড মিসিং হয়, তাহলে বার্তা দেখানো হয়
            if not (selected_batch_id and selected_semester_id and selected_course_id):
                messages.error(request, "⚠️ Please select batch, semester, and course.")
                return redirect('student_enroll')

            # পুরাতন ইনরোলমেন্ট থাকলে সেটি আনা হয়, না থাকলে তৈরি হয়
            try:
                enrollment, created = Enrollment.objects.get_or_create(
                    batch_id=selected_batch_id,
                    semester_id=selected_semester_id,
                    section_id=selected_section_id,
                    course_id=selected_course_id
                )
            except IntegrityError:
                messages.error(request, "❌ Enrollment already exists and could not be processed.")
                return redirect('student_enroll')

            successful_students = []
            # প্রতিটি শিক্ষার্থী ইনরোল করা হচ্ছে যদি আগে না থাকে
            for student_id in selected_ids:
                student = UserRegistration.objects.get(id=student_id)
                if not enrollment.students.filter(id=student.id).exists():
                    enrollment.students.add(student)
                    successful_students.append(student)

            # নির্বাচিত টিচারদের ইনরোল করা হচ্ছে
            for teacher_id in selected_teacher_ids:
                teacher = UserRegistration.objects.get(id=teacher_id)
                if not enrollment.teachers.filter(id=teacher.id).exists():
                    enrollment.teachers.add(teacher)

            # সেশন ক্লিয়ার করা হচ্ছে
            request.session['selected_ids'] = []

            if successful_students:
                messages.success(request, f"✅ {len(successful_students)} student(s) enrolled successfully.")
            else:
                messages.info(request, "ℹ️ All selected students were already enrolled.")

            return redirect('enrolled_student_list')

    # যে ব্যাচগুলোতে ইনরোলমেন্ট হয়েছে তা আনা হচ্ছে
    enrolled_batches = Batch.objects.filter(id__in=Enrollment.objects.values_list('batch_id', flat=True).distinct())

    # টেমপ্লেটের জন্য ডেটা পাঠানো হচ্ছে
    context = {
        'batches': batches,
        'semesters': semesters,
        'sections': sections,
        'courses': courses,
        'students': students,
        'selection_type': selection_type,
        'search_roll': search_roll,
        'batch_filter': batch_filter,
        'selected_ids': selected_ids,
        'selected_students': UserRegistration.objects.filter(id__in=selected_ids),
        'enrolled_batches': enrolled_batches,
        'is_new_assign_mode': is_new_assign_mode,
        'all_teachers': all_teachers,
        'selected_teacher_ids': selected_teacher_ids,
    }

    return render(request, 'education/student_enroll.html', context)


def enrollment_summary(request):
    if not hasattr(request.user, 'role') or request.user.role != UserRegistration.MANAGER:
        messages.warning(request, "⛔ You are not authorized to access this page.")
        return redirect('home')

    enrollments = Enrollment.objects.select_related('batch', 'semester', 'section', 'course') \
        .prefetch_related('students', 'teachers') \
        .order_by('batch__id', 'semester__id', 'section__id', 'course__position_no')

    # ইনরোলমেন্টগুলোকে ব্যাচ, সেমিস্টার এবং সেকশন অনুযায়ী গ্রুপ করা হচ্ছে
    grouped_data = {}
    for enrollment in enrollments:
        batch_id = enrollment.batch.id
        semester_id = enrollment.semester.id
        section_id = enrollment.section.id if enrollment.section else 'no_section'

        if batch_id not in grouped_data:
            grouped_data[batch_id] = {
                'batch': enrollment.batch,
                'semesters': {}
            }

        if semester_id not in grouped_data[batch_id]['semesters']:
            grouped_data[batch_id]['semesters'][semester_id] = {
                'semester': enrollment.semester,
                'sections': {}
            }

        if section_id not in grouped_data[batch_id]['semesters'][semester_id]['sections']:
            grouped_data[batch_id]['semesters'][semester_id]['sections'][section_id] = {
                'section': enrollment.section,
                'entries': []
            }

        grouped_data[batch_id]['semesters'][semester_id]['sections'][section_id]['entries'].append(enrollment)

    # ফর্মসেট তৈরি করা হচ্ছে যাতে একাধিক ইনরোলমেন্ট একসাথে এডিট করা যায়
    EnrollmentFormSet = modelformset_factory(Enrollment, form=EnrollmentEditForm, extra=0)

    if request.method == 'POST':
        formset = EnrollmentFormSet(request.POST, queryset=enrollments)
        if formset.is_valid():
            formset.save()
            messages.success(request, "✅ Enrollment data updated successfully.")
            return redirect('enrollment_summary')
        else:
            messages.error(request, "⚠️ কিছু তথ্য ডুপ্লিকেট বা ভুল রয়েছে। দয়া করে সঠিক করে আবার চেষ্টা করুন।")
    else:
        formset = EnrollmentFormSet(queryset=enrollments)

    # টেমপ্লেট রেন্ডার করা হচ্ছে
    context = {
        'grouped_data': grouped_data,
        'formset': formset,
    }
    return render(request, 'education/enrollment_summary.html', context)


def student_courses(request, student_id):
    if not hasattr(request.user, 'role') or request.user.role != UserRegistration.MANAGER:
        messages.warning(request, "⛔ You are not authorized to access this page.")
        return redirect('home')

    student = get_object_or_404(UserRegistration, id=student_id)

    # ঐ ছাত্রের সব Enrollment আনছি
    enrollments = Enrollment.objects.filter(students=student).select_related(
        'batch', 'semester', 'section', 'course'
    ).prefetch_related('teachers')

    # enriched_enrollments লিস্ট তৈরি করছি যাতে কোর্সের সাথে শিক্ষকের নাম দেখা যায়
    enriched_enrollments = []
    for enrollment in enrollments:
        if enrollment.teachers.exists():
            for teacher in enrollment.teachers.all():
                enriched_enrollments.append({
                    'enrollment': enrollment,
                    'teacher': teacher
                })
        else:
            enriched_enrollments.append({
                'enrollment': enrollment,
                'teacher': None
            })

    context = {
        'student': student,
        'enriched_enrollments': enriched_enrollments,
    }
    return render(request, 'education/student_courses.html', context)



# Teacher

def teacher_wise_student(request):
    if not hasattr(request.user, 'role') or request.user.role != UserRegistration.TEACHER:
        messages.warning(request, "⛔ You are not authorized to access this page.")
        return redirect('home')

    teacher = request.user
    search_roll = request.GET.get('search_roll')
    selected_batch_id = request.GET.get('batch')
    selected_semester_id = request.GET.get('semester')
    selected_section_id = request.GET.get('section')
    selected_course_id = request.GET.get('course')

    teacher_enrollments = Enrollment.objects.filter(teachers=teacher)

    batches = Batch.objects.filter(id__in=teacher_enrollments.values('batch_id').distinct())
    semesters = Semester.objects.filter(id__in=teacher_enrollments.filter(batch_id=selected_batch_id).values('semester_id')) if selected_batch_id else Semester.objects.none()
    sections = Section.objects.filter(id__in=teacher_enrollments.filter(batch_id=selected_batch_id, semester_id=selected_semester_id).values('section_id')) if selected_batch_id and selected_semester_id else Section.objects.none()

    if selected_batch_id and selected_semester_id and selected_section_id:
        if selected_section_id == "none":
            courses = Course.objects.filter(id__in=teacher_enrollments.filter(batch_id=selected_batch_id, semester_id=selected_semester_id, section__isnull=True).values('course_id'))
        else:
            courses = Course.objects.filter(id__in=teacher_enrollments.filter(batch_id=selected_batch_id, semester_id=selected_semester_id, section_id=selected_section_id).values('course_id'))
    else:
        courses = Course.objects.none()

    filters = Q(teachers=teacher)
    if selected_batch_id:
        filters &= Q(batch_id=selected_batch_id)
    if selected_semester_id:
        filters &= Q(semester_id=selected_semester_id)
    if selected_section_id:
        filters &= Q(section__isnull=True) if selected_section_id == "none" else Q(section_id=selected_section_id)
    if selected_course_id:
        filters &= Q(course_id=selected_course_id)

    if search_roll:
        filters &= Q(students__roll_number__icontains=search_roll)

    enrollments = Enrollment.objects.filter(filters).prefetch_related('students', 'batch', 'semester', 'section', 'course')

    students = OrderedDict()
    for enrollment in enrollments:
        for student in enrollment.students.all():
            if search_roll:
                if search_roll.lower() in student.roll_number.lower():
                    students[student.id] = student
            else:
                students[student.id] = student
    student_list = list(students.values())

    # 🔽 Download Excel functionality
    if 'download' in request.GET and student_list:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Enrolled Students"

        ws.append(["Roll Number", "Name", "Email", "Phone", "Batch", "Semester", "Section", "Course"])

        for student in student_list:
            enrollment = Enrollment.objects.filter(
                students=student,
                teachers=teacher,
                batch_id=selected_batch_id,
                semester_id=selected_semester_id,
                course_id=selected_course_id,
            ).first()

            ws.append([
                student.roll_number,
                student.full_name,
                student.email,
                student.mobile_number,
                enrollment.batch.batch_name if enrollment and enrollment.batch else '',
                enrollment.semester.semester_name if enrollment and enrollment.semester else '',
                enrollment.section.section_name if enrollment and enrollment.section else 'None',
                enrollment.course.course_code if enrollment and enrollment.course else '',
            ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="enrolled_students.xlsx"'
        wb.save(response)
        return response

    # Pagination
    paginator = Paginator(student_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'batches': batches,
        'semesters': semesters,
        'sections': sections,
        'courses': courses,
        'students': page_obj,
        'page_obj': page_obj,
        'selected_batch_id': selected_batch_id,
        'selected_semester_id': selected_semester_id,
        'selected_section_id': selected_section_id,
        'selected_course_id': selected_course_id,
        'search_roll': search_roll,
        'show_warning': not search_roll and not (selected_batch_id and selected_semester_id and selected_course_id),
    }
    return render(request, 'teacher/teacher_wise_student.html', context)
