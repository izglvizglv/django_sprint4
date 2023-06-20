from django.conf import settings
from django.conf.urls.static import static
from django.urls import path


from . import views
from .views import e_handler500

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(),
         name='index'),
    path('category/<str:category_slug>/',
         views.CategoryListView.as_view(),
         name='category_posts'),
    path('profile/<username>/',
         views.ShowsProfilePageView.as_view(),
         name='profile'),
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
    path('posts/<int:pk>/delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'),

    path('<int:pk>/comment/',
         views.CommentAddView.as_view(),
         name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),
    path('posts/<post_id>/delete_comment/<comment_id>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),
    # path('<int:pk>/', views.CommentUpdateView.as_view())
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler500 = e_handler500
