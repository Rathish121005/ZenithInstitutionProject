from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from .views import save_test_view

urlpatterns = [
    path('', views.homepage_view, name='homepage'),
    path('admission/', views.admission_view, name='admission'),
    path('login/', views.login_view, name='login'),
    
    path('parentportal/', views.parent_portal_view, name='parentportal'),  
    path('tutor/', views.tutor_portal_view, name='tutor'),
    path('privacy/', views.privacy_view, name='privacy'),  
    path('forgot/', views.forgot_view, name='forgot'),     
    path('contact/', views.contact_view, name='contact'),
    path('tutor/', views.tutor_portal_view, name='tutorportal'),
     path('logout/', views.logout_view, name='logout'),
     
     path('studentportal/', views.student_portal_view, name='studentportal'),
    path('change-password/', views.change_password, name='change_password'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('logout/', views.student_logout, name='student_logout'),
    path('parent-portal/', views.parent_portal_view, name='parent_portal'),
     path('create-test/', views.create_test_view, name='create_test'),
    path('get-marks/', views.get_marks, name='get_marks'),
    path('save-test/', views.save_test_view, name='save_test'),
    path('delete-test/', views.delete_test_view, name='delete_test'),
    path('tutor-logout/', views.tutor_logout, name='tutor_logout'),
    
]
