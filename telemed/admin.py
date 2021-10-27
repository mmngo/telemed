from django.contrib import admin
from .models import Patient, Physician, ConsultationRecord

# Register your models here.

class PhysicianAdmin(admin.ModelAdmin):
	list_display = ('physicianID', 'get_name', 'specialization')

admin.site.register(Physician, PhysicianAdmin)

class PatientAdmin(admin.ModelAdmin):
    list_display = ('patientID', 'get_name', 'date_of_birth')
    
admin.site.register(Patient, PatientAdmin)

class ConsultationRecordAdmin(admin.ModelAdmin):
	list_display = ('recordID', 'patientID', 'physicianID')
admin.site.register(ConsultationRecord, ConsultationRecordAdmin)

