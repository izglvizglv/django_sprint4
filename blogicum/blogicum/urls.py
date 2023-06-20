from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from . import views

from core.views import e_handler500
from core.views import page_not_found

urlpatterns = [
    path('pages/', include('pages.urls', namespace='pages')),
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', views.RegistrationCreateView.as_view(), name='registration'),
    path('auth/', include('blog.urls'))
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)

handler500 = e_handler500
handler404 = page_not_found
