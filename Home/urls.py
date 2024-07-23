from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile', views.profile, name='profile'),
    path('my-bookings', views.my_bookings, name='my_bookings'),
    path('payment-details', views.payment_details, name='payment_details'),
    
    
    
    path('about', views.about, name='about'),
    path('contact-us', views.contact, name='contact'),
    path('login', views.signin, name='login'),
    path('register', views.signup, name='signup'),
    path('logout', views.logout_view,name="logout"),
    path('two-fact-auth', views.otpverify,name="otpverify"),
    path('privacy-policies', views.privacy_policies, name='privacy_policy'),
    path('terms-and-conditions', views.terms, name='terms'),

    
    
    path('available-routes', views.available_routes,name="available_routes"),
    path('book-route', views.book_route,name="book-route"),
    path('view-route/<str:id>', views.view_routes, name='view_routes'),

]