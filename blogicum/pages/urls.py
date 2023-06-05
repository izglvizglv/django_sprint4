from django.urls import path

from . import views

from .views import page_not_found, e_handler500

app_name = 'pages'

urlpatterns = [
    path('about/', views.About.as_view(), name='about'),
    path('rules/', views.Rules.as_view(), name='rules'),
]

handler404 = page_not_found
handler500 = e_handler500
