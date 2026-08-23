from django.urls import path
from . import views

urlpatterns = [
    # This combines with the main urls to create the exact endpoint: /api/register/
    path('register/', views.submit_registration, name='submit_registration'),
    path('login/', views.candidate_login, name='candidate_login'),
]