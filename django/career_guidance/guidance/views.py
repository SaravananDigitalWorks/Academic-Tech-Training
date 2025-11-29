from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Question, Course, StudentResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import *


def home(request):
    return render(request, "guidance/index.html")

def auth_logout(request):
    logout(request)
    return redirect('guidance:home')

@login_required
def questionnaire(request):
    questions = Question.objects.all()
    
    if request.method == "POST":
        for question in questions:
            answer = request.POST.get(str(question.id)) == "yes"
            StudentResponse.objects.update_or_create(
                student=request.user, question=question, defaults={"answer": answer}
            )
        return redirect("guidance:recommendations")

    return render(request, "guidance/questionnaire.html", {"questions": questions})

@login_required
def recommendations(request):
    student_responses = StudentResponse.objects.filter(student=request.user)
    yes_answers = [r.question for r in student_responses if r.answer]

    matched_courses = Course.objects.filter(criteria__in=yes_answers).distinct()

    # Send email
    subject = "Career Guidance Recommendations"
    message = f"Hi {request.user.username},\n\nBased on your responses, we recommend these courses:\n"
    message += "\n".join([course.name for course in matched_courses])
    send_mail(subject, message, "admin@career-guidance.com", [request.user.email])

    return render(request, "guidance/recommendations.html", {"courses": matched_courses})
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user automatically after registration
            return redirect("guidance:dashboard")  # Redirect to the student dashboard
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def dashboard(request):
    if not request.user.is_superuser :
        return render(request, "students/dashboard.html")
    else :
        return redirect("/admin/")

def about_view(request):
    return render(request, "guidance/about.html")

def contact_view(request):
    return render(request, "guidance/contact.html") 

  