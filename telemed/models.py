from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import datetime
import os
import uuid


def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
    return os.path.join("files", filename)


class Physician(models.Model):

    specialties = [
        ('Anesthesiologist', 'Anesthesiologist'),
        ('Cardiologist','Cardiologist'),
        ('Dermatologist', 'Dermatologist'),
        ('Family Physician','Family Physician'),
        ('Internal Medicine Physician','Internal Medicine Physician'),             
        ('Nephrologist', 'Nephrologist'),
        ('OB/GYN','OB/GYN'),
        ('Oncologist','Oncologist'),
        ('Pediatrician','Pediatrician'),
        ('Psychiatrist', 'Psychiatrist'),
        ('Radiologist', 'Radiologist')
    ]

    user 					= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    physicianID             = models.AutoField(primary_key=True)

    profile_pic             = models.ImageField(upload_to='prof_pics/')
    middle_name 			= models.CharField(max_length=20, null=True, blank=True, default=None)
    date_of_birth			= models.DateField()
    address 				= models.CharField(max_length=100)
    mobile 					= models.CharField(max_length=20)
    landline 				= models.CharField(max_length=20, null=True, blank=True)
    specialization 			= models.CharField(max_length=50, choices=specialties)
    hospital_affiliation 	= models.CharField(max_length=200, null=True, blank=True, default=None)
    application_status 		= models.BooleanField(default=False)

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return "{} ({})".format(self.user.first_name, self.specialization)

    def calculate_age(self):
	    today = date.today()
	    return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class Patient(models.Model):
    user 					= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    patientID               = models.AutoField(primary_key=True)

    # profile_pic = models.ImageField(upload_to='profile_pic/DoctorProfilePic/',null=True,blank=True)
    middle_name 			= models.CharField(max_length=20, null=True, blank=True, default=None)
    date_of_birth			= models.DateField()
    address 				= models.CharField(max_length=40)
    mobile 					= models.CharField(max_length=20)
    landline 				= models.CharField(max_length=20, null=True, blank=True)
    assigned_doctor_id 		= models.PositiveIntegerField(null=True, blank=True)
    assigned_doctor_approve = models.BooleanField(default=False)
    application_status 		= models.BooleanField(default=False)

    def calculate_age(self):
	    today = date.today()
	    return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return self.user.first_name


class ConsultationRecord(models.Model):
    recordID                            = models.AutoField(primary_key=True)
    patientID				            = models.PositiveIntegerField()
    patient_document                    = models.FileField(upload_to='patient_document', null=True, blank=True)
    current_medication                  = models.TextField(max_length=500, null=True, blank=True) 
    temperature                         = models.CharField(max_length=20, null=True, blank=True)
    allergies                           = models.TextField(max_length=500, null=True, blank=True)
    presenting_problems                 = models.TextField(max_length=500, null=True, blank=True)
    assessments                         = models.TextField(max_length=500, null=True, blank=True) 
    plan                                = models.TextField(max_length=500, null=True, blank=True)
    lab_request                         = models.FileField(upload_to='lab_request', null=True, blank=True)
    prescription                        = models.FileField(upload_to='prescription', null=True, blank=True)
    consultation_date                   = models.DateField(default=datetime.datetime.now(), null=True, blank=True)
    consultation_time                   = models.TimeField(default=datetime.datetime.now(), null=True, blank=True)
    next_consultation_date              = models.DateField(null=True, blank=True)
    physicianID                         = models.PositiveIntegerField()
    assigned_physician_name             = models.CharField(max_length=100, null=True, blank=True)
    assigned_physician_specialization   = models.CharField(max_length=100, null=True, blank=True)
    patient_modified                    = models.BooleanField(default=False)
    physician_modified                  = models.BooleanField(default=False)