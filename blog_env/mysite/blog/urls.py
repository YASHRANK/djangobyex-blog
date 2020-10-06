from django.urls import path
from . import views
from .feeds import LatestPostsFeed


app_name = 'blog'

urlpatterns = [
    # rss
    path('feed/', LatestPostsFeed(), name='post_feed'),

    path('', views.post_list, name='post_list'),
    path('search/', views.post_search, name='post_search'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('<slug:post>/', views.post_detail,  name='post_detail'),
    path('<str:slug>/share/', views.post_share, name='post_share'),



]
