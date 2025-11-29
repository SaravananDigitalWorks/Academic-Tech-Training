from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import *
from django.utils import timezone
from django.forms import formset_factory
from .forms import *
def home(request) :
    return render(request,'events/index.html')

def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user_registered = EventRegistration.objects.filter(event=event, user=request.user).exists()
    return render(request, 'events/event_detail.html', {'event': event, 'user_registered': user_registered})

@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        return redirect('events:event_detail', event_id=event_id)
    EventRegistration.objects.create(event=event, user=request.user)
    return redirect('events:event_detail', event_id=event_id)

@login_required
def student_dashboard(request):
    user_roles = UserRoleMapping.objects.filter(user=request.user)
    if not user_roles.filter(role__role='student').exists():
        return redirect('events:event_list')
    
    current_events = Event.objects.filter(event_dates__date__gte=timezone.now()).distinct()
    past_events = Event.objects.filter(event_dates__date__lt=timezone.now()).distinct()
    return render(request, 'events/student_dashboard.html', {
        'current_events': current_events,
        'past_events': past_events,
    })

@login_required
def organizer_dashboard(request):
    user_roles = UserRoleMapping.objects.filter(user=request.user)
    if not user_roles.filter(role__role='organizer').exists():
        return redirect('events:event_list')
    
    current_events = Event.objects.filter(event_dates__date__gte=timezone.now()).distinct()
    past_events = Event.objects.filter(event_dates__date__lt=timezone.now()).distinct()
    events = Event.objects.all()
    return render(request, 'events/organizer_dashboard.html', {
        'current_events': current_events,
        'past_events': past_events,
        'events': events,
    })

@login_required
def dashboard(request):
    if not request.user.is_superuser :
        user_roles = UserRoleMapping.objects.filter(user=request.user)
        if user_roles.filter(role__role='student').exists():
            return redirect('events:student_dashboard')
        if user_roles.filter(role__role='organizer').exists():
            return redirect('events:organizer_dashboard')
        if user_roles.filter(role__role='volunteer').exists():
            return redirect('events:volunteer_dashboard')     
        return redirect('events:student_register')
    else :
        return redirect("/admin/")

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            student_role = UserRole.objects.get(role='student')
            UserRoleMapping.objects.create(user=user, role=student_role)
            login(request, user)  # Log in the user automatically after registration
            return redirect("events:dashboard")  # Redirect to the student dashboard
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def edit_event(request, event_id):
    # Check if the user is an organizer
    user_roles = UserRoleMapping.objects.filter(user=request.user)
    if not user_roles.filter(role__role='organizer').exists():
        return redirect('events:event_list')
    
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('events:organizer_dashboard')
    else:
        form = EventForm(instance=event)
    
    return render(request, 'events/edit_event.html', {'form': form, 'event': event})

@login_required
def upload_event_images(request, event_id):
    # Check if the user is an organizer
    user_roles = UserRoleMapping.objects.filter(user=request.user)
    if not user_roles.filter(role__role='organizer').exists():
        return redirect('events:event_list')
    
    event = get_object_or_404(Event, id=event_id)
    if event :
        existing_images = EventImage.objects.filter(event=event)
    if request.method == 'POST':
        form = EventImageForm(request.POST, request.FILES)
        if form.is_valid():
            event_image = form.save(commit=False)
            event_image.event = event
            event_image.save()
            return redirect('events:organizer_dashboard')
    else:
        form = EventImageForm()
    
    return render(request, 'events/upload_event_images.html', {'form': form, 'event': event, 'existing_images': existing_images,})

@login_required
def add_event(request):
    # Check if the user is an organizer
    user_roles = UserRoleMapping.objects.filter(user=request.user)
    if not user_roles.filter(role__role='organizer').exists():
        return redirect('events:event_list')
    
    if request.method == 'POST':
        event_form = EventForm(request.POST)
        date_formset = EventDateFormSet(request.POST, prefix='dates')
        image_formset = EventImageFormSet(request.POST, request.FILES, prefix='images')
        
        if event_form.is_valid() and date_formset.is_valid() and image_formset.is_valid():
            event = event_form.save(commit=False)
            event.created_by = request.user
            event.save()
            
            # Save event dates
            for date_form in date_formset:
                event_date = date_form.save(commit=False)
                event_date.event = event
                event_date.save()
                
                # Save agendas for each event date
                agenda_prefix = f'agendas-{date_form.prefix}'
                agenda_formset = AgendaFormSet(request.POST, prefix=agenda_prefix)
                if agenda_formset.is_valid():
                    for agenda_form in agenda_formset:
                        agenda = agenda_form.save(commit=False)
                        agenda.event_date = event_date
                        agenda.save()
            
            # Save event images
            for image_form in image_formset:
                event_image = image_form.save(commit=False)
                event_image.event = event
                event_image.save()
            
            return redirect('events:organizer_dashboard')
    else:
        event_form = EventForm()
        date_formset = EventDateFormSet(prefix='dates')
        image_formset = EventImageFormSet(prefix='images')
    
    return render(request, 'events/add_event.html', {
        'event_form': event_form,
        'date_formset': date_formset,
        'image_formset': image_formset,
    })
@login_required
def delete_event_image(request, image_id):
    # Check if the user is an organizer
    user_roles = UserRoleMapping.objects.filter(user=request.user)
    if not user_roles.filter(role__role='organizer').exists():
        return redirect('events:event_list')
    
    image = get_object_or_404(EventImage, id=image_id)
    event_id = image.event.id
    image.delete()
    return redirect('events:upload_event_images', event_id=event_id)

def about(request):
    return render(request, 'events/about.html')

def contact(request):
    return render(request, 'events/contact.html')    