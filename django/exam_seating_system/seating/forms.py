from django import forms
from .models import Student, StudentSubjectMapping, Teacher, TeacherSubjectMapping

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_number', 'contact_number', 'email']

class StudentSubjectMappingForm(forms.ModelForm):
    class Meta:
        model = StudentSubjectMapping
        fields = ['student', 'subject']

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'employee_id', 'contact_number', 'email']

class TeacherSubjectMappingForm(forms.ModelForm):
    class Meta:
        model = TeacherSubjectMapping
        fields = ['teacher', 'subject']