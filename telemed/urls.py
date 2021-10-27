from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='homepage'),
    path('aboutus', views.about_us, name='aboutus'),
    path('logout/', views.logout_request, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('password_reset/', views.password_reset, name='password_reset'),


	# Patient urls 
    path('patient_registration/', views.patient_registration, name='patient_registration'),
    path('patient/ask_consultation/<int:pk>', views.ask_for_consultation, name='ask-consultation'),


    # Physician urls
    path('physician_registration/', views.physician_registration, name='physician_registration'),

    path('physician_patient_list/', views.physician_patient_list, name='physician_patient_list'),
    path('physician/patient_info/<int:pk>', views.show_patient_info, name='patient-info'),
    path('physician/confirm_consultation/<int:pk>', views.confirm_consultation, name='confirm-consultation'),
    path('physician/reject_consultation/<int:pk>', views.reject_consultation, name='reject-consultation'),

    path('physician/telemed_doctors/', views.show_telemed_doctors, name='telemed-doctors'),

    path('physician/edit_consultation_record/<int:pk>', views.edit_consultation_record, name='edit-consultation-record'),
    path('physician/view_patient_documents/<int:pk>', views.view_patient_documents, name='view-patient-documents'),
    path('physician/discharge_patient/<int:pk>', views.discharge_patient, name='discharge-patient'),
    

    # System Admin urls
    path('admin/approve_patient/', views.admin_approve_patient, name='admin_approve_patient'),
    path('approve_patient/<int:pk>', views.approve_patient, name='approve_patient'),
    path('reject_patient/<int:pk>', views.reject_patient, name='reject_patient'),

    path('admin/patient_record/', views.admin_patient_record, name='admin_patient_record'),
    path('delete_patient/<int:pk>', views.delete_patient, name='delete_patient'),
    path('deactivate_patient/<int:pk>', views.deactivate_patient, name='deactivate_patient'),

    path('admin/patients/', views.patient_cards, name='patient-card'),
    path('admin/physicians/', views.physician_cards, name='physician-card'),

    path('admin/approve_physician/', views.admin_approve_physician, name='admin_approve_physician'),
    path('approve_physician/<int:pk>', views.approve_physician, name='approve_physician'),
    path('reject_physician/<int:pk>', views.reject_physician, name='reject_physician'),

    path('admin/physician_record/', views.admin_physician_record, name='admin_physician_record'),
    path('delete_physician/<int:pk>', views.delete_physician, name='delete_physician'),
    path('deactivate_physician/<int:pk>', views.deactivate_physician, name='deactivate_physician'),


    # Upload Files Using Model Form
    re_path(r'^download/(?P<file_path>.*)/$', views.file_response_download, name='file_download'),
    re_path(r'^view/(?P<file_path>.*)/$', views.file_response_view, name='file_view'),

]