from django.urls import path

from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('calendar', views.calendar_view, name='calendar'),
    path('byday/<str:date>', views.day_view, name='day_view'),
    path('list', views.list_view, name='list_view'),
    path('recording/<int:pk>', views.single_view, name='single_view'),
    path('genus/<str:genus>', views.genus_view, name=' genus_view'),
    path(
        'species/<str:genus>.<str:species>',
        views.species_view,
        name=' species_view'
    ),
]
