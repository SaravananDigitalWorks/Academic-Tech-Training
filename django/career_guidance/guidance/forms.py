from django import forms
from .models import StudentResponse

class StudentResponseForm(forms.ModelForm):
    class Meta:
        model = StudentResponse
        fields = ['question', 'answer']
