from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('all-users', views.all_users, name='all-users'),
    path('dshboard-login', views.dashboard_login, name='dashboard_login'),
    
    path('bus-info', views.all_buses, name='bus-info'),
    path('bus-details/<str:id>', views.bus_details, name='bus-details'),
    # path('all-bookings', views.dashboard, name='all-bookings'),
    
    
    path('all-routes', views.all_routes, name='all-routes'),
    path('all-boarding-points', views.all_boarding_points, name='all-boarding-points'),
    path('all-dopping-points', views.all_dropping_points, name='all-dropping-points'),
    path('all-facilities', views.all_facilities, name='all-facilities'),


]