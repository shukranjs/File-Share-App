from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('<str:user_name>/upload_file', views.UploadView.as_view(), name='upload_file'),
    path('profile/<str:user_name>', views.ProfileView.as_view(), name='profile'),
    path('delete/<int:post_id>', views.PostDeleteView.as_view(), name='delete'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('share/<int:pk>', views.FileShareListView.as_view(), name='share'), 
    path('file/<int:pk>', views.FileShareDetailView.as_view(), name='file-detail'),
    path('create/<str:content_type>/<int:object_id>/', views.CommentCreateView.as_view(), name='comment-create')
]