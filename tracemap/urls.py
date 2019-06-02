from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('byday/<str:date>', views.day_view, name='day_view'),
]
