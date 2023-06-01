from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(),
         name='index'),
    path('category/<str:category_slug>/',
         views.category_posts,
         name='category_posts'),
    path('profile/<str:username>',
         views.ShowsProfilePageView.as_view(),
         name='profile'),
    path('registration/',
         views.UserRegisterView.as_view(),
         name='registration'),
    path('edit_profile/', views.UserEditView.as_view(), name='edit_profile'),

    path('posts/create/',
         views.PostCreateView.as_view(),
         name='create_post'),
    path('posts/<int:pk>/',
         views.PostDetailView.as_view(),
         name='post_detail'),
    path('posts/<int:pk>/edit/',
         views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/delete/<int:pk>/',
         views.PostDeleteView.as_view(),
         name='delete_post'),

    path('<int:pk>/comment/',
         views.add_comment,
         name='add_comment'),
    path('edit_comment/<int:pk>/',
         views.edit_comment,
         name='edit_comment'),
    path('delete_comment/<int:pk>/',
         views.delete_comment,
         name='delete_comment'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
