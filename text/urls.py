from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<slug:pop>/', views.evolve, name="evolve"),
    path('dashboard/<slug:pop>/', views.dashboard, name="dashboard"),
    path('id/<str:individual>', views.details, name="details"),
]

