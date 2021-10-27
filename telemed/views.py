from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect

from django.contrib.auth.models import Group, User
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Patient, Physician, ConsultationRecord
from .forms import PhysicianUserForm, PhysicianForm, PatientUserForm, PatientForm, ConsultationForm

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .decorators import unauthenticated_user
from django.contrib.auth.decorators import login_required

# for downloading files
import os
import uuid
from django.http import JsonResponse, HttpResponse, Http404, StreamingHttpResponse, FileResponse
from django.template.defaultfilters import filesizeformat


'''	==============================================================		

							FOR ALL USERS			

 =================================================================  '''

@unauthenticated_user
def home(request):
	error_message = ""

	if request.method == 'POST':
		email = request.POST.get('email')
		password = request.POST.get('password')
		user = authenticate(request, email=email, password=password)
		if user is not None:
			login(request, user)
			return redirect('dashboard')
		else:
			error_message = 'Incorrect email or password!'

	context = {
		'error_message': error_message
	}
	return render(request,'telemed/home.html', context)

def about_us(request):
	return render(request, 'telemed/aboutUsPage.html')

@login_required(login_url='homepage')
def dashboard(request):
	doctors = []
	patients = []
	available_doctors = []
	assigned_doctor = []
	patient_requests = []
	num_of_patients_active = 0
	total_num_of_patients = 0
	total_num_of_physicians = 0
	num_of_physician_applicants = 0
	num_of_patient_applicants = 0
	user_group = request.user.groups.all()[0].name
	print("\nCurrent User Group: ",user_group,"\n")

	#for table in patient dashboard
	if user_group == "Patient":
		available_doctors=Physician.objects.all().filter(application_status=True)
		curr_patient_id = request.user.id
		User = get_user_model()
		patientUser = User.objects.get(id=curr_patient_id)
		assigned_id = patientUser.patient.assigned_doctor_id
		assigned_doctor = Physician.objects.all().filter(physicianID=assigned_id)

	#for table in physician dashboard
	if user_group == "Physician":
		curr_physician_id = request.user.id
		User = get_user_model()
		physicianUser = User.objects.get(id=curr_physician_id)
		physician_id = physicianUser.physician.physicianID
		patient_requests = Patient.objects.all().filter(assigned_doctor_id=physician_id).filter(assigned_doctor_approve=False)
		num_of_patients_active = Patient.objects.all().filter(assigned_doctor_id=physician_id).filter(assigned_doctor_approve=True).count()

	#for both table in admin dashboard
	if user_group == "System Admin":
		doctors = Physician.objects.all().order_by('-physicianID')
		total_num_of_physicians = Physician.objects.all().count()
		num_of_physician_applicants = Physician.objects.all().filter(application_status=False).count()
		patients = Patient.objects.all().order_by('-patientID')
		total_num_of_patients = Patient.objects.all().count()
		num_of_patient_applicants = Patient.objects.all().filter(application_status=False).count()

	context = { 'doctors': doctors, 
		'patients': patients, 
		'available_doctors':available_doctors, 
		'patient_requests':patient_requests, 
		'assigned_doctor':assigned_doctor,
		'num_of_patients_active': num_of_patients_active,
		'total_num_of_patients': total_num_of_patients,
		'total_num_of_physicians': total_num_of_physicians,
		'num_of_patient_applicants': num_of_patient_applicants,
		'num_of_physician_applicants': num_of_physician_applicants,
	 }
	return render(request, 'telemed/dashboard.html', context)

def password_reset(request):
	return render(request, 'telemed/password_reset_form.html')


def logout_request(request):
	logout(request)
	messages.success(request, 'You have successfully logged out!')
	return redirect('homepage')

'''	==============================================================		

							FOR PATIENT AND PHYSICIAN			

 =================================================================  '''
@login_required(login_url='homepage')
def show_patient_info(request, pk):

	patient = Patient.objects.get(patientID=pk)
	patient_id = patient.patientID
	user_group = request.user.groups.all()[0].name
	assigned_doctor = []
	consultation_record = []
	consultation_record = ConsultationRecord.objects.all().filter(patientID=patient_id)
	User = get_user_model()
	curr_patientUser = User.objects.filter(patient__patientID=patient_id)

	if user_group == 'Physician':
		curr_physician_id = request.user.id
		User = get_user_model()
		physicianUser = User.objects.get(id=curr_physician_id)
		physician_id = physicianUser.physician.physicianID
		physician_name = physicianUser.first_name + " " + physicianUser.last_name
		physician_specialization = physicianUser.physician.specialization

		curr_physician_id = request.user.physician.physicianID
		patient = Patient.objects.get(patientID = pk)
		patient_id = patient.patientID

		if request.method == 'POST' and 'add-record' in request.POST:
			new_record = ConsultationRecord(patientID=patient_id, physicianID=curr_physician_id, assigned_physician_name=physician_name, assigned_physician_specialization=physician_specialization)
			tempform = ConsultationForm(request.POST, instance=new_record)
			if tempform.is_valid():
				tempform.save()
				messages.success(request, "Added a new consultation record")
			else:
				print("\n\nNOT VALID FORM!\n\n")

	if user_group == 'Patient':
		assigned_doctor_id = patient.assigned_doctor_id
		assigned_doctor = Physician.objects.all().filter(physicianID=assigned_doctor_id)

	context = {'patient':patient, 'assigned_doctor':assigned_doctor, 'consultation_record':consultation_record, 'patientUser':curr_patientUser,}
	return render(request,'telemed/physician_patient_info.html', context)

@login_required(login_url='homepage')
def edit_consultation_record(request, pk):
	record = ConsultationRecord.objects.get(recordID = pk)
	form = ConsultationForm(instance=record)

	# Cancel editing Consultation Form
	if request.method == 'POST' and 'canceleditrecord' in request.POST:
		return redirect('patient-info', pk=record.patientID)

	# Patient Edit Consultation Form
	if request.method == "POST" and "patient_editrecord" in request.POST:
		form = ConsultationForm(request.POST, request.FILES, instance=record)
		if form.is_valid():
			form.save()
			# if patient doc is not empty, save upload
			if request.FILES.get('pd_upload') != None:
				myfile = request.FILES.get('pd_upload', False)
				record.patient_document = myfile
				record.save()
			record.patient_modified = True
			record.save()
			messages.success(request, "Record has been saved")
			return redirect('patient-info', pk=record.patientID)
		else: 
			print("\nCANNOT SAVED\n")

	# Physician Edit Consultation Form
	if request.method == "POST" and "physician_editrecord" in request.POST:
		form = ConsultationForm(request.POST, request.FILES, instance=record)
		if form.is_valid():
			form.save()
			# if lab request upload is not empty, save upload
			if request.FILES.get('lr_upload') != None:
				myfile = request.FILES.get('lr_upload', False)
				record.lab_request = myfile
				record.save()
			# if prescription upload is not empty, save upload
			if request.FILES.get('pres_upload') != None:
				myfile = request.FILES.get('pres_upload', False)
				record.prescription = myfile
				record.save()	
			record.physician_modified = True
			record.save()
			messages.success(request, "Record has been saved")
			return redirect('patient-info', pk=record.patientID)
		else: 
			print("\nCANNOT SAVED\n")

	context = {
		'form': form,
		'record': record

	}
	return render(request, 'telemed/consultation_form.html', context)

# for downloading documents uploaded by patient and physician
@login_required(login_url='homepage')
def file_response_download(request, file_path):
    ext = os.path.basename(file_path).split('.')[-1].lower()
    # cannot be used to download py, db and sqlite3 files.
    if ext not in ['py', 'db',  'sqlite3']:
        response = FileResponse(open(file_path, 'rb'))
        response['content_type'] = "application/octet-stream"
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
        return response
    else:
        raise Http404

@login_required(login_url='homepage')
def file_response_view(request, file_path):
    ext = os.path.basename(file_path).split('.')[-1].lower()
    # cannot be used to download py, db and sqlite3 files.
    if ext not in ['py', 'db',  'sqlite3']:
        response = FileResponse(open(file_path, 'rb'))
        response['content_type'] = "application/octet-stream"
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        return response
    else:
        raise Http404


'''	==============================================================		

							PATIENT			

 =================================================================  '''
@unauthenticated_user
def patient_registration(request):
	userForm = PatientUserForm()
	patientForm = PatientForm()

	if request.method=='POST':
		userForm = PatientUserForm(request.POST)
		patientForm = PatientForm(request.POST)
		if userForm.is_valid() and patientForm.is_valid():
			user = userForm.save()
			user.set_password(user.password)
			user.save()
			patient = patientForm.save(commit=False)
			patient.user = user
			patient = patient.save()
			my_patient_group = Group.objects.get_or_create(name='Patient')
			my_patient_group[0].user_set.add(user)
			messages.success(request, 'Registration submitted')
			return redirect('patient_registration')
	
	context = { 'userForm': userForm,'patientForm':patientForm }
	return render(request,'telemed/patient_registration.html', context)

@login_required(login_url='homepage')
def ask_for_consultation(request, pk):
	patient_id = request.user.id
	User = get_user_model()
	patientUser = User.objects.get(id=patient_id)
	patientUser.patient.assigned_doctor_id = pk
	patientUser.patient.save()
	messages.success(request, "Consultation request sent")
	return redirect('dashboard')


'''	==============================================================		

							PHYSICIAN			

 =================================================================  '''
@unauthenticated_user
def physician_registration(request):
	userForm = PhysicianUserForm()
	physicianForm = PhysicianForm()

	if request.method=='POST':
		userForm = PhysicianUserForm(request.POST)
		physicianForm = PhysicianForm(request.POST, request.FILES)
		if userForm.is_valid() and physicianForm.is_valid():
			user = userForm.save()
			user.set_password(user.password)
			user.save()
			physician = physicianForm.save(commit=False)
			physician.user = user
			# mypic = request.FILES.get('pp_upload', False)
			# physician.profile_pic = mypic
			physician = physician.save()
			my_physician_group = Group.objects.get_or_create(name='Physician')
			my_physician_group[0].user_set.add(user)
			messages.success(request, 'Registration submitted')
			return redirect('physician_registration')
	
	context = { 'userForm': userForm,'physicianForm':physicianForm }
	return render(request,'telemed/physician_registration.html', context)

def show_telemed_doctors(request):
	available_doctors=Physician.objects.all().filter(application_status=True)
	context = {
	'available_doctors':available_doctors,
	 }
	return render(request, 'telemed/telemed_doctors.html', context)

@login_required(login_url='homepage')
def physician_patient_list(request):
	curr_physician_id = request.user.physician.physicianID
	patients = Patient.objects.all().filter(assigned_doctor_id=curr_physician_id).filter(assigned_doctor_approve=True)
	context = {'patients':patients}
	return render(request,'telemed/physician_patientList.html', context)

@login_required(login_url='homepage')
def reject_consultation(request, pk):
	patient = Patient.objects.get(patientID=pk)
	patient.assigned_doctor_id = None
	patient.save()
	messages.error(request, "Consultation denied")
	return redirect('dashboard')

@login_required(login_url='homepage')
def confirm_consultation(request, pk):
	patient = Patient.objects.get(patientID=pk)
	patient.assigned_doctor_approve = True
	patient.save()
	messages.success(request, "Consultation confirmed")
	return redirect('dashboard')

@login_required(login_url='homepage')
def add_consultation_record(request, pk):
	curr_physician_id = request.user.physician.physicianID
	patient = Patient.objects.get(patientID = pk)
	patient_id = patient.patientID

	if request.method == 'POST' and 'add-record' in request.POST:
		new_record = ConsultationRecord(patientID=patient_id, physicianID=curr_physician_id, consultation_date=currentDate, consultation_time=currentTime)
		tempform = ConsultationForm(request.POST, instance=new_record)
		if tempform.is_valid():
			tempform.save()
			messages.success(request, "Added a new consultation record")

	new_record = ConsultationRecord(patientID=patient_id, physicianID=curr_physician_id, consultation_date=currentDate, consultation_time=currentTime)
	if new_record.is_valid():
		new_record.save()
		messages.success(request, "Added a new consultation record")

	return redirect('patient-info', pk=pk)

@login_required(login_url='homepage')
def discharge_patient(request, pk):
	patient = Patient.objects.get(patientID=pk)
	patient.assigned_doctor_id = None
	patient.assigned_doctor_approve = False
	patient.save()
	messages.success(request, "Successfully discharged patient")
	return redirect('physician_patient_list')


'''	==============================================================		

							SYSTEM ADMIN			

 =================================================================  '''

### 	Patient Navigation
@login_required(login_url='homepage')
def patient_cards(request):
	return render(request, 'telemed/admin_patient_card.html')

@login_required(login_url='homepage')
def deactivate_patient(request,pk):
	patient = Patient.objects.get(patientID=pk)
	patient.application_status = False
	patient.assigned_doctor_id = None
	patient.assigned_doctor_approve = False
	patient.save()
	messages.success(request, 'Account deactivated')
	return redirect('admin_patient_record')

@login_required(login_url='homepage')
def delete_patient(request, pk):
	patient=Patient.objects.get(patientID=pk)
	User = get_user_model()
	user = User.objects.get(id=patient.user_id)
	user.delete()
	patient.delete()
	messages.success(request, 'Account successfully deleted')
	return redirect('admin_patient_record')

@login_required(login_url='homepage')
def admin_patient_record(request):
	patients=Patient.objects.all().filter(application_status=True)
	context = { 'patients': patients }
	return render(request,'telemed/admin_patient_record.html', context)

@login_required(login_url='homepage')
def approve_patient(request,pk):
	patient = Patient.objects.get(patientID=pk)
	patient.application_status=True
	patient.save()
	messages.success(request, 'Account approved')
	return redirect('admin_approve_patient')

@login_required(login_url='homepage')
def reject_patient(request, pk):
	patient=Patient.objects.get(patientID=pk)
	User = get_user_model()
	user = User.objects.get(id=patient.user_id)
	user.delete()
	patient.delete()
	messages.success(request, 'Account successfully deleted')
	return redirect('admin_approve_patient')

@login_required(login_url='homepage')
def admin_approve_patient(request):
	patients=Patient.objects.all().filter(application_status=False)
	context = { 'patients': patients }
	return render(request,'telemed/admin_approve_patients.html', context)


### 	Physician Navigation
@login_required(login_url='homepage')
def physician_cards(request):
	return render(request, 'telemed/admin_doctor_card.html')
	
@login_required(login_url='homepage')
def deactivate_physician(request,pk):
	doctor = Physician.objects.get(physicianID=pk)
	doctor.application_status = False
	doctor.save()
	messages.success(request, 'Account deactivated')
	return redirect('admin_physician_record')

@login_required(login_url='homepage')
def delete_physician(request,pk):
	doctor = Physician.objects.get(physicianID=pk)
	User = get_user_model()
	user = User.objects.get(id=doctor.user_id)
	user.delete()
	doctor.delete()
	messages.success(request, 'Account successfully deleted')
	return redirect('admin_physician_record')

@login_required(login_url='homepage')
def admin_physician_record(request):
	doctors=Physician.objects.all().filter(application_status=True)
	context = { 'doctors': doctors }
	return render(request,'telemed/admin_physician_record.html', context)


@login_required(login_url='homepage')
def approve_physician(request,pk):
    doctor = Physician.objects.get(physicianID=pk)
    doctor.application_status=True
    doctor.save()
    messages.success(request, 'Account approved')
    return redirect('admin_approve_physician')

@login_required(login_url='homepage')
def reject_physician(request,pk):
	doctor = Physician.objects.get(physicianID=pk)
	User = get_user_model()
	user = User.objects.get(id=doctor.user_id)
	user.delete()
	doctor.delete()
	messages.success(request, 'Account successfully deleted')
	return redirect('admin_approve_physician')

@login_required(login_url='homepage')
def admin_approve_physician(request):
	doctors=Physician.objects.all().filter(application_status=False)
	context = { 'doctors': doctors }
	return render(request,'telemed/admin_approve_physicians.html', context)








# NOT FINAL / NEED TO EDIT
@login_required(login_url='homepage')
def view_patient_documents(request, pk):
	pass