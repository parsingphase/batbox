from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('calendar', views.calendar, name='calendar'),
    path('byday/<str:date>', views.day, name='day_view'),
    path('list', views.list_all, name='list_view'),
    path('recording/<int:pk>', views.single, name='single_view'),
    path('genus/<str:genus_name>', views.genus, name='genus_view'),
    path(
        'species/<str:genus_name>.<str:species_name>',
        views.species,
        name='species_view'
    ),
    path('search', views.search, name='search_view'),
    path('api/search', views.search_api, name='search_api'),
    path('img/species_marker/<str:genus_name>.<str:species_name>', views.species_marker, name='species_marker'),
]
