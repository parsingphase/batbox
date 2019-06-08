from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('byday/<str:date>', views.day_view, name='day_view'),
    path('list', views.list_view, name='list_view'),
    path('recording/<int:pk>', views.single_view, name='single_view'),
]
