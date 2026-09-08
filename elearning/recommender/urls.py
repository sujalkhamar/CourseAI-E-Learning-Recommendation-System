from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('recommend/', views.recommend, name='recommend'),
    path('analytics/', views.analytics, name='analytics'),
    path('explore/', views.explore, name='explore'),
    path('api/skills/', views.autocomplete_skills, name='autocomplete'),
]
