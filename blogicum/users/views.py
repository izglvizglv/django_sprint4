from django.shortcuts import get_object_or_404
from django.views import generic
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView
from blog.models import Profile
from django.contrib.auth import get_user_model



class UserRegisterView(generic.CreateView):
    form_class = UserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')


class UserEditView(generic.UpdateView):
    form_class = UserChangeForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return self.request.user


class ShowProfilePageView(DetailView):
    model = get_user_model()
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'blog/profile.html'

    def get_object(self, queryset=None):
        user_object = (get_user_model().objects.filter(username=self.kwargs.get(self.slug_url_kwarg)))
        object = get_object_or_404(klass=user_object)
        return object
