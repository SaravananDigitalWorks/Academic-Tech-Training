from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import *
from .forms import *
from django.contrib.auth.models import User, Group
def home(request):
    return render(request,'attendance/index.html')

def about(request):
    return render(request, 'attendance/about.html')

def contact(request):
    return render(request, 'attendance/contact.html')

@login_required
def mark_attendance(request, class_id):
    class_obj = Class.objects.get(id=class_id)
    # Fetch students assigned to this class using ClassStudentMapping
    student_mappings = ClassStudentMapping.objects.filter(class_name=class_obj)
    students = [mapping.student for mapping in student_mappings]
    
    if request.method == 'POST':
        date = request.POST.get('date')
        session = request.POST.get('session')
        for student in students:
            status = 'P' if request.POST.get(f'status_{student.id}') else 'A'
            Attendance.objects.update_or_create(
                student=student, class_name=class_obj, date=date, session=session,
                defaults={'status': status}
            )
        return redirect('attendance:attendance_summary', class_id=class_id)
    return render(request, 'attendance/mark_attendance.html', {'class_obj': class_obj, 'students': students})

@login_required
def attendance_summary(request, class_id):
    class_obj = Class.objects.get(id=class_id)
    # Fetch students assigned to this class using ClassStudentMapping
    student_mappings = ClassStudentMapping.objects.filter(class_name=class_obj)
    students = [mapping.student for mapping in student_mappings]
    
    holidays = Holiday.objects.filter(date__gte=class_obj.start_date, date__lte=class_obj.end_date).count()
    total_days = (class_obj.end_date - class_obj.start_date).days - holidays
    attendance_data = []
    for student in students:
        present_days = Attendance.objects.filter(student=student, status='P').count()
        percentage = (present_days / (total_days * 2)) * 100 if total_days > 0 else 0
        attendance_data.append({
            'student': student,
            'present_days': present_days,
            'percentage': round(percentage, 2)
        })
    return render(request, 'attendance/attendance_summary.html', {'class_obj': class_obj, 'attendance_data': attendance_data})

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()     
            # student_group, created = Group.objects.get_or_create(name='Student')
            # user.groups.add(student_group)       
            login(request, user)  
            return redirect("attendance:dashboard")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def dashboard(request):
    print(request.user)
    if not request.user.is_superuser :
        if request.user.groups.filter(name='Student').exists():
            return redirect('attendance:student_dashboard')
        if request.user.groups.filter(name='Teacher').exists():
            return redirect('attendance:teacher_dashboard')
        return redirect('attendance:student_register')
    else :
        return redirect("/admin/")

@login_required
def student_dashboard(request):
    # Get the logged-in student
    student = Student.objects.get(user=request.user)
    
    # Get all classes the student is enrolled in
    class_mappings = ClassStudentMapping.objects.filter(student=student)
    classes = [mapping.class_name for mapping in class_mappings]
    
    # Calculate attendance summary for each class
    attendance_summary = []
    for class_obj in classes:
        # Get holidays for the class duration
        holidays = Holiday.objects.filter(date__gte=class_obj.start_date, date__lte=class_obj.end_date).count()
        
        # Calculate total working days (excluding holidays)
        total_days = (class_obj.end_date - class_obj.start_date).days - holidays
        
        # Get attendance records for the student in this class
        attendance_records = Attendance.objects.filter(student=student, class_name=class_obj)
        
        # Calculate present and absent days
        present_days = attendance_records.filter(status='P').count()
        absent_days = attendance_records.filter(status='A').count()
        
        # Calculate attendance percentage
        percentage = (present_days / (total_days * 2)) * 100 if total_days > 0 else 0
        
        # Add class attendance summary to the list
        attendance_summary.append({
            'class': class_obj,
            'total_days': total_days * 2,  # Morning and evening sessions
            'present_days': present_days,
            'absent_days': absent_days,
            'percentage': round(percentage, 2)
        })
    
    return render(request, 'student/dashboard.html', {'attendance_summary': attendance_summary})


@login_required
def teacher_dashboard(request):    
    if request.user.groups.filter(name='Teacher').exists():
        teacher = Teacher.objects.get(user=request.user)
        class_mappings = ClassTeacherMapping.objects.filter(teacher=teacher)
        classes = [mapping.class_name for mapping in class_mappings]
        return render(request,'teacher/dashboard.html', {'classes': classes})
    else:
        return redirect('attendance:home')

@login_required
def student_register(request):
    if request.user.groups.filter(name='Student').exists():
            return redirect('attendance:dashboard')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.user = request.user
            student.save()
            student_group, created = Group.objects.get_or_create(name='Student')
            request.user.groups.add(student_group)
            return redirect('attendance:student_dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'attendance/student_register.html', {'form': form})
    