from django.urls import path
from . import views

urlpatterns = [
    path('carparks/', views.carpark_list, name='carpark_list'),
    path('carparks/vacancy/', views.carpark_vacancy, name='carpark_vacancy'),
    path('carparks/districts/', views.districts, name='districts'),
    path('config/mapbox-token/', views.mapbox_token, name='mapbox_token'),
    path('favorites/', views.favorite_list, name='favorite_list'),
    path('favorites/add/', views.favorite_add, name='favorite_add'),
    path('favorites/check/<str:carpark_id>/', views.favorite_check, name='favorite_check'),
    path('favorites/<str:carpark_id>/', views.favorite_remove, name='favorite_remove'),
]
