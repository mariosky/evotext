
from django.urls import path

from . import views

urlpatterns = [
    path('admin', views.index, name='index'),
    path('initialize', views.initialize, name='initialize'),
    path('<slug:population>/sample/<int:size>/', views.sample),
    path('<slug:population>/sample/', views.sample),
]

