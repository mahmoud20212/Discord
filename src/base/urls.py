from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('room/<str:pk>/', views.room, name='room_detail'),
    path('create-room/', views.create_room, name='create-room'),
    path('update-room/<str:pk>/', views.update_room, name='update-room'),
    path('delete-room/<str:pk>/', views.delete_room, name='delete-room'),
    path('delete-message/<str:pk>/', views.delete_message, name='delete-message'),
    path('topics/', views.topics_page, name='topics'),
    path('activity/', views.activity_page, name='activity'),
    # user
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('profile/<str:pk>/', views.user_profile, name='user-profile'),
    path('update-user/', views.update_user, name='update-user'),
    path('logout/', views.user_logout, name='logout'),
]