
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import Physician, Patient, ConsultationRecord
from datetime import date
import datetime

class DateInput(forms.DateInput):
	input_type = 'date'

#for physician registration
class PhysicianUserForm(forms.ModelForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput( attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput( attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        user=get_user_model()
        model=user
        fields=['first_name','last_name','email','password']
        widgets = {
            'email': forms.TextInput( attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            self.add_error('confirm_password', "Password does not match")
        return cleaned_data

class PhysicianForm(forms.ModelForm):
    class Meta:
        model = Physician
        exclude = ['application_status', 'user']
        widgets = {
            'middle_name': forms.TextInput( attrs={'class': 'form-control'}),
        	'date_of_birth': DateInput( attrs={'class': 'form-control'}),
            'address': forms.TextInput( attrs={'class': 'form-control'}),
            'mobile': forms.NumberInput( attrs={'class': 'form-control'}),
            'landline': forms.NumberInput( attrs={'class': 'form-control'}),
            'specialization': forms.Select( attrs={'class': 'form-control'}),
            'hospital_affiliation': forms.TextInput( attrs={'class': 'form-control'}),
            'profile_pic': forms.ClearableFileInput( attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()
        date_of_birth = cleaned_data.get("date_of_birth")

        today = date.today()
        if date_of_birth > today:
            self.add_error('date_of_birth', "Date should not be greater than today")
        return cleaned_data


#for patient registration
class PatientUserForm(forms.ModelForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput( attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput( attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        user=get_user_model()
        model=user
        fields=['first_name','last_name','email','password']
        widgets = {
            'email': forms.TextInput( attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            self.add_error('confirm_password', "Password does not match")
        return cleaned_data

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = ['user', 'application_status', 'assigned_doctor_id', 'assigned_doctor_approve']
        widgets = {
        	'middle_name': forms.TextInput( attrs={'class': 'form-control'}),
            'date_of_birth': DateInput( attrs={'class': 'form-control'}),
            'address': forms.TextInput( attrs={'class': 'form-control'}),
            'mobile': forms.NumberInput( attrs={'class': 'form-control'}),
            'landline': forms.NumberInput( attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_of_birth = cleaned_data.get("date_of_birth")

        today = date.today()
        if date_of_birth > today:
            self.add_error('date_of_birth', "Date should not be greater than today")
        return cleaned_data


# Consultation Record
class ConsultationForm(forms.ModelForm):
    class Meta:
        model = ConsultationRecord
        exclude = ['patientID', 'physicianID', 'recordID', 'assigned_physician_name', 'assigned_physician_specialization','patient_modified','physician_modified']
        widgets = {
            'patient_document': forms.ClearableFileInput( attrs={'class': 'form-control'}),
            'current_medication':forms.Textarea(attrs={'rows': 5, 'style': 'width: 99% !important; border-radius: 5px;', 'class': 'form-control'}),
            'temperature':forms.NumberInput(attrs={'rows': 1, 'style': 'width: 99% !important; border-radius: 5px;', 'class': 'form-control'}),
            'allergies' :forms.Textarea(attrs={'rows': 5, 'style': 'width: 99% !important; border-radius: 5px;', 'class': 'form-control'}),
            'presenting_problems':forms.Textarea(attrs={'rows': 5, 'style': 'width: 99% !important; border-radius: 5px;', 'class': 'form-control'}),
            'assessments' :forms.Textarea(attrs={'rows': 5, 'style': 'width: 99% !important; border-radius: 5px;', 'class': 'form-control'}),
            'plan':forms.Textarea(attrs={'rows': 5, 'style': 'width: 99% !important; border-radius: 5px;', 'class': 'form-control'}),
            'lab_request':forms.ClearableFileInput( attrs={'class': 'form-control'}),
            'prescription':forms.ClearableFileInput( attrs={'class': 'form-control'}),
            'consultation_date': forms.DateInput(format=('%Y-%m-%d'), attrs={'class': 'form-control'}),
            'consultation_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'next_consultation_date': forms.DateInput(format=('%Y-%m-%d'), attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'
                }),
        }
