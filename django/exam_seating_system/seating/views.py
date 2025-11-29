from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.contrib.auth.forms import *
from django.contrib.auth import *
from django.contrib.admin.views.decorators import *


def home(request):
     return render(request, 'seating/index.html')

def about(request):
    return render(request, 'seating/about.html')

def contact(request):
    return render(request, 'seating/contact.html')

@login_required
def add_student(request):
    if hasattr(request.user, 'student'):
        return redirect('seating:dashboard')
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.user = request.user
            student.save()
            return redirect('seating:dashboard')
    else:
        form = StudentForm()
        return render(request, 'seating/student_register.html', {'form': form})

@login_required
def student_list(request):
    students = Student.objects.all()
    return render(request, 'seating/student_list.html', {'students': students})

@login_required
def add_student_subject_mapping(request):
    if request.method == 'POST':
        form = StudentSubjectMappingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_subject_mapping_list')
    else:
        form = StudentSubjectMappingForm()
    return render(request, 'seating/add_student_subject_mapping.html', {'form': form})

@login_required
def student_subject_mapping_list(request):
    mappings = StudentSubjectMapping.objects.all()
    return render(request, 'seating/student_subject_mapping_list.html', {'mappings': mappings})

@login_required
def add_teacher(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('teacher_list')
    else:
        form = TeacherForm()
    return render(request, 'seating/add_teacher.html', {'form': form})

@login_required
def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, 'seating/teacher_list.html', {'teachers': teachers})

@login_required
def add_teacher_subject_mapping(request):
    if request.method == 'POST':
        form = TeacherSubjectMappingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('teacher_subject_mapping_list')
    else:
        form = TeacherSubjectMappingForm()
    return render(request, 'seating/add_teacher_subject_mapping.html', {'form': form})

@login_required
def teacher_subject_mapping_list(request):
    mappings = TeacherSubjectMapping.objects.all()
    return render(request, 'seating/teacher_subject_mapping_list.html', {'mappings': mappings})

@login_required
def dashboard(request):
    if not request.user.is_superuser :
        if hasattr(request.user, 'student'):
            return redirect('seating:student_dashboard')  
        if hasattr(request.user, 'teacher'):
            return redirect('seating:teacher_dashboard')
        else:
            return redirect('seating:add_student')
    else :
        return redirect("/admin/")
    

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user automatically after registration
            return redirect("seating:dashboard")  # Redirect to the student dashboard
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})
         
@login_required
def student_dashboard(request):
    if hasattr(request.user, 'student'):
        student = request.user.student
        seating = SeatingArrangement.objects.filter(student=student)
        return render(request, 'seating/student_dashboard.html',{'student':student,'seating':seating})
    return redirect('seating:student_register')  

@login_required
def teacher_dashboard(request):
    if hasattr(request.user, 'teacher'):
        teacher = request.user.teacher
        subjects = TeacherSubjectMapping.objects.filter(teacher=teacher)
        return render(request, 'seating/teacher_dashboard.html',{'teacher':teacher,'subjects':subjects})

@staff_member_required
def map_seating(request):
    if request.method == 'POST':
        exam_halls = ExamHall.objects.all()
        for exam_hall in exam_halls:
            # Call the seat mapping logic here
            map_seating_arrangement(None, request, [exam_hall])
        messages.success(request, "Seating arrangement mapped successfully.")
    return redirect('admin:seating_examhall_changelist')

    