from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Volunteer
    path('volunteer/dashboard/', views.volunteer_dashboard, name='volunteer_dashboard'),
    path('volunteer/profile/', views.volunteer_profile, name='volunteer_profile'),
    path('volunteer/edit-profile/', views.edit_profile, name='edit_profile'),
    path('volunteer/change-password/', views.change_password, name='change_password'),
    
    # NSS Leader
    path('leader/dashboard/', views.leader_dashboard, name='leader_dashboard'),
    path('leader/pending/', views.pending_volunteers, name='pending_volunteers'),
    path('leader/approve/<int:user_id>/', views.approve_volunteer, name='approve_volunteer'),
    path('leader/reject/<int:user_id>/', views.reject_volunteer, name='reject_volunteer'),
    path('leader/approved/', views.approved_volunteers, name='approved_volunteers'),
    path('leader/volunteer/<int:id>/', views.leader_view_volunteer_profile, name='leader_view_volunteer_profile'),
    path('leader/schedule-event/', views.schedule_event, name='schedule_event'),
    path('leader/send-notification/', views.leader_send_notification, name='leader_send_notification'),
    path('leader/notifications/', views.leader_notifications, name='leader_notifications'),

    
    # Admin
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/volunteers/', views.volunteer_list, name='volunteer_list'),
    path('admin/nssleaders/', views.nssleader_list, name='nssleader_list'),
    path('admin/make-leader/<int:id>/', views.make_leader, name='make_leader'),
    path('admin/send-notification/', views.admin_send_notification, name='admin_send_notification'),

    # Blood Bank
    path('bloodbank/', views.bloodbank_list, name='bloodbank_list'),
    path('volunteer/bloodbank/register/', views.volunteer_bloodbank_register, name='volunteer_bloodbank_register'),
    path('leader/bloodbank/register/', views.leader_bloodbank_register, name='leader_bloodbank_register'),

    # Pledge & Certificates
    path('volunteer/pledge/', views.volunteer_pledge, name='volunteer_pledge'),
    path('volunteer/certificates/', views.volunteer_certificates, name='volunteer_certificates'),
    path('volunteer/events/', views.volunteer_events, name='volunteer_events'),
    path('volunteer/notifications/', views.volunteer_notifications, name='volunteer_notifications'),
    path('leader/pledge/', views.leader_pledge, name='leader_pledge'),
    path('leader/certificates/', views.leader_certificates, name='leader_certificates'),
    path('certificate/<int:id>/', views.view_certificate, name='view_certificate'),
]
