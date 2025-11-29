from django import forms
from .models import Student, HostelApplication

class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_number', 'contact_number', 'email']

class HostelApplicationForm(forms.ModelForm):
    class Meta:
        model = HostelApplication
        fields = ['preferred_hostel_building', 'preferred_room_type', 'requires_ac', 'requires_physically_challenged_friendly']