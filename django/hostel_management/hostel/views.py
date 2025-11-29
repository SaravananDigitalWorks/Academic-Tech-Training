from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import StudentRegistrationForm, HostelApplicationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import *


def home(request):
    return render(request, "hostel/index.html")

def about(request):
    return render(request, "hostel/about.html")

def contact(request):
    return render(request, "hostel/contact.html")

# Student Registration
@login_required
def student_register(request):
    if hasattr(request.user, 'student'):
            return redirect('hostel:student_dashboard')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.user = request.user
            student.save()
            return redirect('hostel:student_dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'hostel/student_register.html', {'form': form})

# Hostel Application
@login_required
def apply_hostel(request):
    student = request.user.student
    if request.method == 'POST':
        form = HostelApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = student
            application.save()
            return redirect('hostel:student_dashboard')
    else:
        form = HostelApplicationForm()
    return render(request, 'hostel/apply_hostel.html', {'form': form})

# Student Dashboard
@login_required
def student_dashboard(request):
    if hasattr(request.user, 'student'):
        application = HostelApplication.objects.filter(student=request.user.student).first()
        return render(request, 'hostel/student_dashboard.html', {'application': application})
    return redirect('hostel:student_register')    

# Warden Dashboard
@login_required
def warden_dashboard(request):
    applications = HostelApplication.objects.filter(status='Pending')
    return render(request, 'hostel/warden_dashboard.html', {'applications': applications})

# Approve Application
@login_required
def approve_application(request, application_id):
    application = get_object_or_404(HostelApplication, id=application_id)
    if application.status == 'Pending':
        room = Room.objects.filter(
            is_available=True,
            is_ac=application.requires_ac,
            is_single=(application.preferred_room_type == 'Single'),
            is_physically_challenged_friendly=application.requires_physically_challenged_friendly
        ).first()
        if room:
            application.allotted_room = room
            application.status = 'Approved'
            room.is_available = False
            room.save()
            application.save()
    return redirect('hostel:warden_dashboard')

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user automatically after registration
            return redirect("hostel:dashboard")  # Redirect to the student dashboard
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def dashboard(request):
    if not request.user.is_superuser :
        if hasattr(request.user, 'student'):
            return redirect('hostel:student_dashboard')  
        if hasattr(request.user, 'warden'):
            return redirect('hostel:warden_dashboard')
        else:
            return redirect('hostel:student_register')
    else :
        return redirect("/admin/")