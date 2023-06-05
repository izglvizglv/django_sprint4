from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.core.paginator import Paginator
from .forms import ProfileForm
from django.utils import timezone
from .forms import PostForm, CommentForm
from .models import Category, Comment, Post
from django.contrib.auth import get_user_model
from django.template.defaulttags import register
from django.db.models import Count
from django.template import RequestContext
from django.http import HttpResponseForbidden
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        query = Post.objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,).order_by("-pub_date")
        if self.request.user.is_authenticated:
            query = query | Post.objects.all().filter(
                author_id=self.request.user.pk,
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now(),
            ).order_by("-pub_date")
        query = query.annotate(comment_count=Count('comments'))
        paginator = Paginator(query, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = super().get_context_data(**kwargs)
        context.update({'page_obj': page_obj})

        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = self.object.comments.filter(post=self.object.id)
        context.update({
            'form': CommentForm(),
            'comments': comments,
        })
        return context


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if CommentForm(request.POST).is_valid():
        comment = CommentForm(request.POST).save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ('title', 'text', 'pub_date', 'image', 'location', 'category')
    template_name = 'blog/create.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get(self, request, *args, **kwargs):
        p = Post.objects.filter(pk=kwargs['pk'])
        if len(p) == 0 or self.request.user.pk == p[0].author_id:
            return super().get(request, *args, **kwargs)
        return redirect('blog:post_detail', pk=kwargs['pk'])

    def post(self, request, *args, **kwargs):
        p = Post.objects.filter(pk=kwargs['pk'])
        if len(p) == 0 or self.request.user.pk == p[0].author_id:
            return super().post(request, *args, **kwargs)
        return redirect('blog:post_detail', pk=kwargs['pk'])


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    success_url = reverse_lazy('blog:index')

    def get(self, request, *args, **kwargs):
        p = Post.objects.filter(pk=kwargs['pk'])
        if len(p) == 0 or self.request.user.pk == p[0].author_id:
            return super().get(request, *args, **kwargs)
        return redirect('blog:post_detail', pk=kwargs['pk'])

    def post(self, request, *args, **kwargs):
        p = Post.objects.filter(pk=kwargs['pk'])
        if len(p) == 0 or self.request.user.pk == p[0].author_id:
            return super().post(request, *args, **kwargs)
        return redirect('blog:post_detail', pk=kwargs['pk'])


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts_list = category.posts.all().filter(
        is_published=True,
        pub_date__lte=timezone.now()).order_by("-pub_date")
    if request.user.is_authenticated:
        posts_list = posts_list | category.posts.all().filter(
            author_id=request.user.pk,
            is_published=True,
            pub_date__lte=timezone.now()).order_by("-pub_date")
    posts_list = posts_list.annotate(comment_count=Count('comments'))
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj,
        }

    return render(request, 'blog/category.html', context)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    form = CommentForm(request.POST or None, instance=comment)
    context = {'form': form, 'comment': comment}
    if request.user != comment.author:
        return HttpResponseForbidden(
            'Вам нельзя редактировать данный комментарий!')
    if form.is_valid():
        comment = form.save(commit=False)
        comment.save()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    context = {'comment': comment}
    if request.user != comment.author:
        return HttpResponseForbidden('Вам нельзя удалять данный комментарий!')
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)


class ShowsProfilePageView(DetailView):
    model = get_user_model()
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'blog/profile.html'
    queryset = get_user_model().objects
    context_object_name = 'profile'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        posts = self.object.posts.select_related('author').filter(
            pub_date__lte=timezone.now(), is_published=True
            ).order_by("-pub_date")
        if self.request.user.is_authenticated:
            posts = posts | self.object.posts.filter(
                author_id=self.request.user.pk).order_by("-pub_date")
        posts = posts.annotate(comment_count=Count('comments'))
        paginator = Paginator(posts, 10)
        request = self.request
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = super().get_context_data(**kwargs)
        context.update({'page_obj': page_obj})

        return context


class UserEditView(generic.UpdateView):
    form_class = ProfileForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            return HttpResponse('Unauthorized', status=401)
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


def e_handler500(request):
    context = RequestContext(request)
    response = render('pages/500.html', context)
    response.status_code = 500
    return response
