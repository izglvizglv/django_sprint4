from django.urls import path
from django.contrib import admin
from .views import UserRegisterView, UserEditView, ShowProfilePageView


app_name = 'users'

urlpatterns = [
    path('registration/', UserRegisterView.as_view(), name='registration'),
    path('edit_profile/', UserEditView.as_view(), name='edit_profile'),
    path('profile/<slug:username>',
         ShowProfilePageView.as_view(),
         name='profile'),
]
