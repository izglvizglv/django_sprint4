from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.utils import timezone

from .forms import PostForm, CommentForm
from .models import Category, Comment, Post, User


class PostListView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Записываем в переменную form пустой объект формы.
        context['form'] = CommentForm()
        # Запрашиваем все поздравления для выбранного дня рождения.
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostCreateView(CreateView):
    model = Post
    template_name = 'blog/create.html'
    fields = '__all__'


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts_list = category.posts.all().filter(
        is_published=True,
        pub_date__lt=timezone.now())
    context = {'category': category, 'page_obj': posts_list}
    return render(request, 'blog/category.html', context)


def edit_profile(request, username):
    pass


class CommentCreateView(LoginRequiredMixin, CreateView):
    post = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.author = self.request.user
        form.instance.post = self.post
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', kwargs={'pk': self.post.pk})


@login_required
def edit_comment(request, post_pk, pk):
    context = {}
    context['post_pk'] = post_pk
    context['pk'] = pk
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', context=context)


@login_required
def delete_comment(request, id, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.delete()
    return redirect('blog:post_detail', id=id, pk=pk)
