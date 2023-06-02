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



@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        query = Post.objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True)
        if self.request.user.is_authenticated:
            query = query | Post.objects.all().filter(
                author_id=self.request.user.pk)
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
    form = CommentForm

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            post = self.get_object()
            form.instance.author = request.user
            form.instance.post = post
            form.save()
            return redirect(reverse('post', kwargs={
                'pk': post.pk
            }))

    def get_context_data(self, **kwargs):
        post_comments_count = Comment.objects.all().filter(
            post=self.object.id).count()
        comments = Comment.objects.all().filter(post=self.object.id)
        context = super().get_context_data(**kwargs)
        context.update({
            'form': self.form,
            'comments': comments,
            'post_comments_count': post_comments_count
        })
        return context


class PostCreateView(CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def post(self, request, *args, **kwargs):
        self.post.author.id = self.request.user.pk
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
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
    if request.user.is_authenticated:
        posts_list = posts_list | category.posts.all().filter(
            author_id=request.user.pk)
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
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    form = CommentForm(request.POST or None, instance=comment)
    context = {'form': form, 'comment': comment}
    if form.is_valid():
        comment = form.save(commit=False)
        comment.save()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    form = CommentForm(instance=comment)
    context = {'form': form, 'comment': comment}
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
            pub_date__lte=timezone.now(), is_published=True)
        if self.request.user.is_authenticated:
            posts = posts | self.object.posts.filter(
                author_id=self.request.user.pk)
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
