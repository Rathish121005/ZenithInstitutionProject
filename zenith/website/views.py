from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash
from .models import Admission, Tutor, Student, TestMark, Feedback
from django.shortcuts import render
from .forms import AdmissionForm,ContactForm
from .models import Contact
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Tutor, Student
from django.contrib.auth import logout 
from .models import Feedback
from django.conf import settings
from django.http import JsonResponse
from .models import TestMark
from django.shortcuts import get_object_or_404
from .forms import TestCreationForm, MarkEntryForm
from django.core.cache import cache
from django_ratelimit.decorators import ratelimit

 
# Homepage
def homepage_view(request):
    return render(request, 'homepage.html')

# Admission Form
def admission_view(request):
    if request.method == 'POST':
        form = AdmissionForm(request.POST)
        if form.is_valid():
            admission = form.save()

            # Email setup (your existing email code)
            subject = "🎓 New Admission Form Submitted"
            data = form.cleaned_data
            message = (
                f"                  Zenith Brain Education          \n"
                f"🎓 *New Admission Form Submission*\n\n"
                f"📌 *Personal Details:*\n"
                f"• Name: {data['Name']}\n"
                f"• Date of Birth: {data['DOB']}\n"
                f"• Class: {data['Class']}\n"
                f"• Group: {data.get('Course', 'N/A')}\n\n"
                f"👪 *Parent Details:*\n"
                f"• Mother's Name: {data['MotherName']}\n"
                f"• Father's Name: {data['FatherName']}\n\n"
                f"🏫 *Academic Details:*\n"
                f"• School Name: {data['SchoolName']}\n\n"
                f"📍 *Contact Details:*\n"
                f"• Address: {data['Address']}\n"
                f"• Phone Number: {data['Number']}\n"
                f"• Email: {data.get('Email', 'Not Provided')}\n"
            )

            send_mail(
                subject,
                message,
                'aarockyarathishraj2005@gmail.com',
                ['deepakramaswamy13@gmail.com'],
                fail_silently=False,
            )

            messages.success(request, "Application submitted successfully!")
            return redirect('admission')  # Remove ?success=true parameter
    else:
        form = AdmissionForm()


    success = request.GET.get('success') == 'true'
    return render(request, 'admission.html', {'form': form, 'success': success})
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Student, Tutor, Parent

@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, 'Please enter both username and password')
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                # Check user role and corresponding profile exists
                if user.role == 'student':
                    # Verify student profile exists
                    try:
                        student = Student.objects.get(user=user)
                        login(request, user)
                        return redirect('studentportal')
                    except Student.DoesNotExist:
                        messages.error(request, 'Student profile not found. Please contact administrator.')
                        return render(request, 'login.html')
                
                elif user.role == 'tutor':
                    # Verify tutor profile exists
                    try:
                        tutor = Tutor.objects.get(UserId=user)
                        login(request, user)
                        return redirect('tutor')
                    except Tutor.DoesNotExist:
                        messages.error(request, 'Tutor profile not found. Please contact administrator.')
                        return render(request, 'login.html')
                
                elif user.role == 'parent':
                    # Verify parent profile exists
                    try:
                        parent = Parent.objects.get(UserId=user)
                        login(request, user)
                        return redirect('parentportal')
                    except Parent.DoesNotExist:
                        messages.error(request, 'Parent profile not found. Please contact administrator.')
                        return render(request, 'login.html')
                
                else:
                    # Invalid or unset role
                    messages.error(request, 'Invalid user role. Please contact administrator.')
                    return render(request, 'login.html')
                    
            except AttributeError:
                # User model doesn't have role field
                messages.error(request, 'User role not configured. Please contact administrator.')
                return render(request, 'login.html')
                
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'login.html')

    return render(request, 'login.html')
    

# Portals


def parent_portal_view(request):
    return render(request, 'studentportal.html')  # Changed from student_portal.html

@login_required
def tutor_portal_view(request):
    tutor = get_object_or_404(Tutor, UserId=request.user)
    students = Student.objects.select_related('user').filter(Class=tutor.AssignedClass)
    
    # Get all tests created by this tutor
    tests = TestMark.objects.select_related('student').filter(
        created_by=request.user,
        student__Class=tutor.AssignedClass
    ).values('test_name', 'subject').distinct().prefetch_related('student')
    
    student_data = []
    for student in students:
        test_data = {}
        test_results = TestMark.objects.filter(student=student)
        for result in test_results:
            if result.test_name not in test_data:
                test_data[result.test_name] = {}
            test_data[result.test_name][result.subject] = result.mark
        
        student_data.append({
            'Name': student.Name,
            'Class': student.Class,
            'Group': student.Group,
            'user': student.user,
            'SchoolName': student.SchoolName,
            'Email': student.Email,
            'PhoneNumber': student.PhoneNumber,
            'tests': test_data
        })
    
    return render(request, 'tutor.html', {
        'tutor': tutor,
        'students': student_data,
        'tests': tests
    })

@login_required
def create_test_view(request):
    tutor = get_object_or_404(Tutor, UserId=request.user)
    students = Student.objects.filter(Class=tutor.AssignedClass)
    
    if request.method == 'POST':
        test_form = TestCreationForm(request.POST)
        mark_form = MarkEntryForm(students, request.POST)
        
        if test_form.is_valid() and mark_form.is_valid():
            test_name = test_form.cleaned_data['test_name']
            subject = test_form.cleaned_data['subject']
            
            # Save marks for each student
            for student in students:
                mark_field = f'mark_{student.user.username}'
                mark = mark_form.cleaned_data.get(mark_field)
                
                if mark is not None:
                    TestMark.objects.update_or_create(
                        student=student,
                        test_name=test_name,
                        subject=subject,
                        defaults={
                            'mark': mark,
                            'created_by': request.user
                        }
                    )
            
            messages.success(request, f"Test '{test_name}' created successfully!")
            return redirect('tutor')
    else:
        test_form = TestCreationForm()
        mark_form = MarkEntryForm(students)
    
    return render(request, 'create_test.html', {
        'test_form': test_form,
        'mark_form': mark_form,
        'students': students,
        'tutor': tutor
    })



@login_required
def logout_view(request):
    user_role = getattr(request.user, 'role', None)
    logout(request)
    return redirect('login')

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import render

@login_required
def student_portal_view(request):
    student = request.user.student
    cache_key = f'student_tests_{student.user.username}'
    grouped_tests = cache.get(cache_key)

    if grouped_tests is None:
        test_results = TestMark.objects.filter(student=student).order_by('-test_name')
        grouped_tests = {}
        for result in test_results:
            grouped_tests.setdefault(result.test_name, []).append(result)
        cache.set(cache_key, grouped_tests, timeout=300)  # Cache for 5 minutes

    return render(request, "studentportal.html", {
        "student": student,
        "grouped_tests": grouped_tests,
        "role": "student"
    })


@login_required
def parent_portal_view(request):
    student = request.user.student  # assuming OneToOne or ForeignKey to User
    test_results = TestMark.objects.filter(student=student).order_by('-created_at')

    grouped_tests = {}
    for result in test_results:
        if result.test_name not in grouped_tests:
            grouped_tests[result.test_name] = []
        grouped_tests[result.test_name].append(result)

    return render(request, "studentportal.html", {
        "student": student,
        "grouped_tests": test_results,
        "role": "parent"  # ✅ Add this line
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('currentPassword')
        new_password = request.POST.get('newPassword')
        
        # Check if current password is correct
        if not request.user.check_password(current_password):
            return JsonResponse({'success': False, 'error': 'Current password is incorrect'})
        
        # Set new password
        request.user.set_password(new_password)
        request.user.save()
        
        # Keep user logged in after password change
        update_session_auth_hash(request, request.user)
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
@login_required
def submit_feedback(request):
    if request.method == "POST":
        feedback_text = request.POST.get('feedback')
        if feedback_text:
            try:
                # Save to DB
                Feedback.objects.create(user=request.user, message=feedback_text)
                
                # Send email
                send_mail(
                    subject=f"Feedback from {request.user.username}",
                    message=feedback_text,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=["zenithbraininstitution2022@gmail.com"],
                    fail_silently=False,
                )
                messages.success(request, "Feedback sent successfully.")
                
            except Exception as e:
                messages.error(request, f"Error occurred: {str(e)}")
                
            return redirect("studentportal")
        else:
            messages.error(request, "Feedback cannot be empty.")
    return redirect("studentportal")



# Misc Views
def forgot_view(request):
    return render(request, 'forgot.html')

def privacy_view(request):
    return render(request, 'privacy.html')

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        phone = request.POST.get('phone')

        if not name or not email or not message:
            messages.error(request, "All fields are required.")
            return redirect('contact')

        # Save contact message to the database
        contact = Contact(name=name, email=email, message=message, phone=phone)
        contact.save()
        subject = "Contact Form Submission"
        messagess=(
            f"Dear {name},\n\n"
            f"Thank you for reaching out to us. We will get back to you soon.\n\n"
            f"Best regards,\nZenith Brain Education Team")
        # Send confirmation email
        send_mail(
            subject,
            messagess,
            'aarockyarathishraj2005@gmail.com',
            ['deepakramaswamy13@gmail.com'],
            fail_silently=False,
             )
        send_mail(
            subject,
            f"New contact form submission:\n\n"
            f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}",
            '{email}',
            ['deepakramaswamy13@gmail.com'],
            fail_silently=False,
        )
        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Student

@csrf_exempt
def save_test(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        student_id = data.get('userId')
        test_name = data.get('testName')
        marks = data.get('marks')  # Dictionary: {subject: mark}

        try:
            student = Student.objects.get(user__username=student_id)
            for subject, mark in marks.items():
                TestMark.objects.update_or_create(
                    student=student,
                    test_name=test_name,
                    subject=subject,
                    defaults={'marks': mark}
                )
            return JsonResponse({'status': 'success'})
        except Student.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Student not found'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def student_logout(request):
    logout(request)
    return redirect('login')
def tutor_logout(request):
    logout(request)
    return redirect('login')

@login_required
def create_test_view(request):
    tutor = get_object_or_404(Tutor, UserId=request.user)
    students = Student.objects.filter(Class=tutor.AssignedClass)
    
    if request.method == 'POST':
        test_name = request.POST.get('test_name')
        subjects_str = request.POST.get('subjects')
        
        if not test_name or not subjects_str:
            messages.error(request, 'Test name and subjects are required.')
            return redirect('create_test')
        
        # Parse subjects
        subjects = [s.strip() for s in subjects_str.split(',') if s.strip()]
        
        if not subjects:
            messages.error(request, 'Please enter at least one subject.')
            return redirect('create_test')
        
        # Save marks for each student and subject
        saved_count = 0
        for student in students:
            for subject in subjects:
                mark_field = f'mark_{student.user.username}_{subject}'
                mark_value = request.POST.get(mark_field)
                
                if mark_value and mark_value.strip():
                    try:
                        mark = float(mark_value)
                        TestMark.objects.update_or_create(
                            student=student,
                            test_name=test_name,
                            subject=subject,
                            defaults={
                                'mark': mark,
                                'created_by': request.user
                            }
                        )
                        saved_count += 1
                    except ValueError:
                        continue
        
        if saved_count > 0:
            messages.success(request, f"Test '{test_name}' created successfully! {saved_count} marks saved.")
        else:
            messages.warning(request, "Test created but no marks were saved.")
        
        return redirect('tutor')
    
    return render(request, 'create_test.html', {
        'students': students,
        'tutor': tutor
    })

# Fix the get_marks view
@login_required
def get_marks(request):
    try:
        if hasattr(request.user, 'student'):
            student = request.user.student
            test_name = request.GET.get('test_name')
            
            # Optimize query with select_related
            query = TestMark.objects.select_related('student__user').filter(student=student)
            
            if test_name:
                query = query.filter(test_name=test_name)
            
            # Use values to reduce data transfer
            marks = query.values('subject', 'mark', 'test_name', 'created_at')
            
            return JsonResponse(list(marks), safe=False)
        else:
            return JsonResponse([], safe=False)
            
    except Exception as e:
        return JsonResponse({'error': 'Unable to fetch marks'}, status=500)


# Remove duplicate save_test_view functions and keep only this one:
@login_required
@csrf_exempt
def save_test_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('userId')
            test_name = data.get('testName')
            marks = data.get('marks')  # {subject: mark}
            
            student = Student.objects.get(user__username=user_id)
            
            for subject, mark in marks.items():
                TestMark.objects.update_or_create(
                    student=student,
                    test_name=test_name,
                    subject=subject,
                    defaults={
                        'mark': float(mark),
                        'created_by': request.user
                    }
                )
            
            return JsonResponse({'status': 'success'})
            
        except Student.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Student not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def delete_test_view(request):
    if request.method == 'POST':
        try:
            tutor = get_object_or_404(Tutor, UserId=request.user)
            test_name = request.POST.get('test_name')
            subject = request.POST.get('subject')
            
            if not test_name:
                return JsonResponse({'success': False, 'error': 'Test name is required'})
            
            # Build filter conditions
            filter_conditions = {
                'created_by': request.user,
                'test_name': test_name,
                'student__Class': tutor.AssignedClass
            }
            
            # Add subject filter if provided
            if subject:
                filter_conditions['subject'] = subject
            
            # Delete marks for this test
            deleted_count = TestMark.objects.filter(**filter_conditions).delete()[0]
            
            if deleted_count > 0:
                subject_text = f' for subject "{subject}"' if subject else ''
                return JsonResponse({
                    'success': True, 
                    'message': f'Test "{test_name}"{subject_text} deleted successfully! ({deleted_count} marks removed)'
                })
            else:
                return JsonResponse({'success': False, 'error': 'Test not found or you do not have permission to delete it'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

