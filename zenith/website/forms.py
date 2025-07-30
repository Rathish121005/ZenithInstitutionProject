from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.validators import RegexValidator
from .models import Admission


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        label="User ID",
        widget=forms.TextInput(attrs={'placeholder': 'Enter User ID'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}),
        label="Password"
    )


class AdmissionForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = [
            'Name',
            'DOB',
            'Class',
            'Course',
            'MotherName',
            'FatherName',
            'SchoolName',
            'Address',
            'Number',
            'Email',
            'termsCheck',
        ]

        widgets = {
            'Name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Name'}),
            'DOB': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'Class': forms.Select(attrs={'class': 'form-select', 'onchange': 'toggleCourseField()'}),
            'Course': forms.Select(attrs={'class': 'form-select', 'id': 'course'}),
            'MotherName': forms.TextInput(attrs={'class': 'form-control'}),
            'FatherName': forms.TextInput(attrs={'class': 'form-control'}),
            'SchoolName': forms.TextInput(attrs={'class': 'form-control'}),
            'Address': forms.TextInput(attrs={'class': 'form-control'}),
            'Number': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': '[6-9]{1}[0-9]{9}',
                'maxlength': '10',
                'placeholder': 'Enter 10-digit mobile number'
            }),
            'Email': forms.EmailInput(attrs={'class': 'form-control'}),
            'termsCheck': forms.CheckboxInput(attrs={'class': 'form-check-input', 'required': True}),
        }

    def clean(self):
        cleaned_data = super().clean()
        class_name = cleaned_data.get("Class")
        course = cleaned_data.get("Course")

        if class_name in ['11th', '12th'] and not course:
            self.add_error('Course', "Course selection is required for 11th and 12th class.")

        return cleaned_data


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Name'}),
        error_messages={'required': 'Name is required.'}
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Email'}),
        error_messages={'required': 'Email is required.'}
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Your Message'}),
        error_messages={'required': 'Message is required.'}
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        validators=[RegexValidator(r'^[6-9]\d{9}$', message='Enter a valid 10-digit Indian mobile number')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Phone Number'})
    )

from django import forms
from .models import Student

class TestCreationForm(forms.Form):
    test_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Test Name'})
    )
    subjects = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter subjects separated by commas (e.g., Math, Physics, Chemistry)'
        }),
        help_text="Enter multiple subjects separated by commas"
    )

class MarkEntryForm(forms.Form):
    def __init__(self, students, subjects, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for student in students:
            for subject in subjects:
                field_name = f'mark_{student.user.username}_{subject.strip()}'
                self.fields[field_name] = forms.FloatField(
                    label=f'{student.Name} - {subject.strip()}',
                    required=False,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control mark-input',
                        'min': '0',
                        'max': '100',
                        'step': '0.1',
                        'placeholder': '0'
                    })
                )



