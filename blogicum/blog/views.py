from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import (
    get_object_or_404, HttpResponseRedirect, redirect, render, reverse)
from django.template import RequestContext
from django.template.defaulttags import register
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView)

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post, User


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        page_obj = Post.objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).order_by("-pub_date")
        if self.request.user.is_authenticated:
            page_obj = page_obj | Post.objects.all().filter(
                author_id=self.request.user.pk,
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now(),
            ).order_by("-pub_date")
        return page_obj.annotate(comment_count=Count('comments'))


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        p = Post.objects.filter(pk=kwargs['pk'])
        if self.request.user.id != p[0].author_id and p[0].is_published == 0:
            return redirect('blog:index')
        if self.request.user.id != p[0].author_id and p[0].pub_date > timezone.now():
            return redirect('blog:index')
        else:
            return super(PostDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = self.object.comments.filter(post=self.object.id)
        context.update({
            'form': CommentForm(),
            'comments': comments,
        })
        return context


class CommentAddView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['text']

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse('blog:post_detail', kwargs={'pk': pk})

    def form_valid(self, form):
        form.instance.post_id = self.kwargs['pk']
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})

    def dispatch(self, request, *args, **kwargs):
        p = Post.objects.filter(pk=kwargs['pk'])
        if self.request.user.id != p[0].author_id:
            return redirect('blog:post_detail', self.kwargs['pk'])
        else:
            return super(PostUpdateView, self).dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        if self.object.author_id != self.request.user.id:
            return redirect('blog:post_detail', self.kwargs['pk'])
        self.object.delete()
        return HttpResponseRedirect(success_url)


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'

    def get_context_data(self, **kwargs):
        query = Post.objects.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__slug=self.kwargs['category_slug'],
        ).order_by('-pub_date')
        if self.request.user.is_authenticated:
            query = query | query.filter(
                author_id=self.request.user.pk,
                is_published=True,
                pub_date__lte=timezone.now()
            ).order_by('-pub_date').annotate(comment_count=Count('comments'))
        paginator = Paginator(query, 10)
        page_number = self.request.GET.get('page')
        query = paginator.get_page(page_number)
        context = super().get_context_data(**kwargs)
        context.update({
            'page_obj': query,
            'category': get_object_or_404(Category,
                                          slug=self.kwargs['category_slug'],
                                          is_published=True)})
        return context


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    fields = ['text']
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return Comment.objects.get(pk=self.kwargs.get('comment_id'))

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['post_id']})

    def dispatch(self, request, *args, **kwargs):
        p = Comment.objects.filter(pk=kwargs['comment_id'])
        if self.request.user.id != p[0].author_id:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        else:
            return super().dispatch(request, *args, **kwargs)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    fields = ['text']
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        comment = get_object_or_404(Comment, pk=self.kwargs.get('comment_id'))
        return comment

    def get_success_url(self):
        return reverse('blog:index')

    def delete(self, request, *args, **kwargs):
        comment = self.get_object()
        success_url = self.get_success_url()
        if comment.author_id != self.request.user.id:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        comment.delete()
        return HttpResponseRedirect(success_url)


class ShowsProfilePageView(DetailView):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'blog/profile.html'
    queryset = User.objects
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        page_obj = self.object.posts.select_related(
            'author').filter(pub_date__lte=timezone.now(), is_published=True
                             ).order_by('-pub_date')
        if self.request.user.is_authenticated:
            page_obj = page_obj | self.object.posts.filter(
                author_id=self.request.user.pk).order_by('-pub_date')
        page_obj = page_obj.annotate(comment_count=Count('comments'))
        paginator = Paginator(page_obj, 10)
        request = self.request
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = super().get_context_data(**kwargs)
        context.update({'page_obj': page_obj})
        return context


class UserEditView(LoginRequiredMixin, generic.UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'username', 'email')
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


def e_handler500(request):
    context = RequestContext(request)
    response = render('pages/500.html', context)
    response.status_code = 500
    return response
