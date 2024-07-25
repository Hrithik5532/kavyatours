from django.urls import path
from . import views

urlpatterns = [
  
    path('book-route', views.book_route,name="book-route"),
    
    
    path('payment-status', views.payment_status,name="payment_status"),

]