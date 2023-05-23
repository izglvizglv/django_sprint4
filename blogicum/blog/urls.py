from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(),
         name='index'),
    path('category/<str:category_slug>/',
         views.category_posts,
         name='category_posts'),


    path('posts/create/',
         views.PostCreateView.as_view(),
         name='create_post'),
    path('posts/<int:pk>/',
         views.PostDetailView.as_view(),
         name='post_detail'),
    path('posts/edit/<int:pk>/',
         views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/delete/<int:pk>/',
         views.PostDeleteView.as_view(),
         name='delete_post'),

    path('posts/<int:pk>/comment/',
         views.CommentCreateView.as_view(),
         name='add_comment'),
    path('posts/<int:id>/edit_comment/<int:pk>/',
         views.CommentCreateView.as_view(),
         name='edit_comment'),
    path('posts/<int:id>/delete_comment/<int:pk>/',
         views.delete_comment,
         name='delete_comment'),
]
