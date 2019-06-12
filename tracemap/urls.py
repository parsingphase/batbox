from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('calendar', views.calendar, name='calendar'),
    path('byday/<str:date>', views.day, name='day_view'),
    path('list', views.list_all, name='list_view'),
    path('recording/<int:pk>', views.single, name='single_view'),
    path('genus/<str:genus>', views.genus, name=' genus_view'),
    path(
        'species/<str:genus>.<str:species>',
        views.species,
        name=' species_view'
    ),
    path('search', views.search, name=' search_view'),

]
