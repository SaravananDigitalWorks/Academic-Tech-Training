from django import forms
from django.forms import inlineformset_factory
from .models import *

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description']

class EventImageForm(forms.ModelForm):
    class Meta:
        model = EventImage
        fields = ['image']

class EventDateForm(forms.ModelForm):
    class Meta:
        model = EventDate
        fields = ['date']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'datepicker', 'autocomplete': 'off'}),
        }

class AgendaForm(forms.ModelForm):
    class Meta:
        model = Agenda
        fields = ['title', 'start_time', 'end_time']

# Inline formsets
EventDateFormSet = inlineformset_factory(Event, EventDate, form=EventDateForm, extra=1, can_delete=True)
AgendaFormSet = inlineformset_factory(EventDate, Agenda, form=AgendaForm, extra=1, can_delete=True)
EventImageFormSet = inlineformset_factory(Event, EventImage, form=EventImageForm, extra=1, can_delete=True)