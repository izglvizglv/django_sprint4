from django.conf import settings
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.template import RequestContext
from django.urls import include, path, reverse_lazy
from django.views.generic.edit import CreateView

urlpatterns = [
    path('pages/', include('pages.urls', namespace='pages')),
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/',
         CreateView.as_view(
             template_name='registration/registration_form.html',
             form_class=UserCreationForm, success_url=reverse_lazy('login')),
         name='registration'),
    path('auth/', include('blog.urls'))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)


def e_handler500(request):
    context = RequestContext(request)
    response = render('pages/500.html', context)
    response.status_code = 500
    return response


def handler404(request, exception, template_name="pages/404.html"):
    response = render(request, template_name)
    response.status_code = 404
    return response


handler500 = e_handler500
handler404 = handler404
