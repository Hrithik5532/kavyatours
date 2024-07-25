from django.shortcuts import render,redirect

# Create your views here.
from django.contrib import messages
from .models import *
import requests
def book_route(request):
    if request.method == 'POST':
        route_id = request.POST.get('routeID')
        seat_number = request.POST.get('selectedSeats').split(',')
        print(route_id,seat_number)
        bus = NewRoute.objects.get(id=route_id)
        price = bus.base_price
        total = price * len(seat_number)
        
        payment = PaymentDetails.objects.create(
            customer_name = request.user.name,
            customer_phone = request.user.phone,
            customer_email = request.user.email,
            customer_address = request.user.address,
            payment_status = 'Pending',
            payment_amount = total,
            
        )
        payment.save()
        
        body = {
            "key": "0135af3f-8086-40fe-aa1f-92d3660c26f7",
            "client_txn_id": payment.id,
            "amount": str(total),
            "p_info": str(bus.id),
            "customer_name": str(request.user.name),
            "customer_email": "jondoe@gmail.com",
            "customer_mobile": str(request.user.phone),
            "redirect_url": "https://test.trizyn.com/payment/payment-status?order_id="+str(bus.id),
            "udf1": "user defined field 1 (max 25 char)",
            "udf2": "user defined field 2 (max 25 char)",
            "udf3": "user defined field 3 (max 25 char)"
            }
        
        req = requests.post('https://api.ekqr.in/api/create_order', json=body)
        try:
            if req.status_code == 200:
                data = req.json()
                print(data)
                payment.payment_id = data['data']['order_id']
                payment.upi_response = data
                payment.save()
                if data['status']:
                    return redirect(data['data']['payment_url'])
                else:
                    messages.error(request, 'Something went wrong. Please try again.')
                    return redirect(request.META.get('HTTP_REFERER'))
            else:
                messages.error(request, 'Something went wrong. Please try again.')
                return redirect(request.META.get('HTTP_REFERER'))
        except:
            messages.error(request, 'Something went wrong. Please try again.')
        # messages.success(request, 'Route booked successfully.')
            return redirect(request.META.get('HTTP_REFERER'))

def payment_status(request):
    
    return render(request, 'bookingpage-success.html')
