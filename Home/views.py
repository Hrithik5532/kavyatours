from django.shortcuts import render,redirect
from django.contrib import messages
from .models import Contact
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *
import random
from RouteDir.models import *
from datetime import datetime, timedelta
import requests


def home(request):
    boardingpoint = BoardingPoints.objects.all()
    droppingpoints = DroppingPoints.objects.all()
    
    allroutes = NewRoute.objects.order_by('-boarding_date').all()
    routes_with_last_dropping = []
    for route in allroutes:
        last_dropping_point = route.get_last_dropping_point()
        travel_duration = route.get_travel_duration()
        try :
            booked_seats = route.booked_seats.split(',')
        except:
            booked_seats = []
        
        routes_with_last_dropping.append({
            'route': route,
            'last_dropping_point': last_dropping_point,
            'travel_duration': travel_duration,
            'available_seats': int(route.total_seats) - int( len(booked_seats))
        })
    return render(request, 'index.html',{'boardingpoint':boardingpoint,'droppingpoints':droppingpoints,'buses':routes_with_last_dropping})

def profile(request):
    if not request.user.is_authenticated :
        return redirect('signup')
    user = User.objects.get(phone=request.user.phone)

    if request.method == 'POST':
        if request.GET.get('option') == 'changepass':
            otp = request.POST.get('otp')
            pass1 = request.POST.get('pass1')
            pass2 = request.POST.get('pass2')
            
            if int(request.user.otp) == int(otp):
                if pass1 == pass2:
                
                    user.set_password(pass1)
                    user.save()
                    login(request, user)
                    messages.success(request, 'Password changed successfully.')
                    return redirect('profile')
                else:
                    messages.error(request, 'Passwords do not match.')
                    return redirect('profile')
            else:
                messages.error(request, 'Invalid OTP.')
                return redirect('profile')
        
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        dob = request.POST.get('dob')
        user.name = name
        user.phone = phone
        user.email = email
        user.address = address
        user.dob = dob
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    
    if request.user.name and request.user.phone and request.user.is_verified and request.user.email and request.user.address not in ['',None] and request.user.dob:
        profile_complete = True
    else:
        profile_complete = False
    return render(request, 'my-profile-main.html',{'profile_complete':profile_complete})


def my_bookings(request):
    if not request.user.is_authenticated:
        return redirect('signup')
    return render(request, 'my-booking.html')

def payment_details(request):
    if not request.user.is_authenticated:
        return redirect('signup')
    return render(request, 'payment-detail.html')

def logout_view(request):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER'))

def SendOTP(phone):
    otp = random.randint(1000, 9999)
    user = User.objects.get(phone=phone)
    user.otp = otp
    user.save()




def signin(request):
    if request.method == 'POST':
        username = request.POST.get('phone')
        password = request.POST.get('password')

        if len(username) == 10 and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if not request.user.is_verified:  # Assuming there's a profile related to user with is_verified field
                    SendOTP(username)
                    return redirect('otpverify')
                else:
                    return redirect(request.META.get('HTTP_REFERER'))
            else:
                messages.error(request, 'Invalid username or password.')
                return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Please enter a valid phone number and password.')
            return redirect(request.META.get('HTTP_REFERER'))



def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('phone')
        phone = request.POST.get('phone')
        name = request.POST.get('name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if len(username) == 10 and password == confirm_password:
            user = User.objects.create_user(username=username, phone=phone, name=name, password=password)
            user.save()
            messages.success(request, 'Account created successfully.')
            login(request, user)
            SendOTP(username)

            return redirect('otpverify')
        else:
            messages.error(request, 'Please enter a valid phone number and password.')
            return redirect('home')  # Redirecting to home to allow reattempt
    return render(request, 'register.html')




def otpverify(request):
    if request.GET.get('resendotp')=='true':
        SendOTP(request.user.phone)
        messages.success(request, 'OTP sent successfully.')
        return redirect(request.META.get('HTTP_REFERER'))

    if request.method == 'POST':
        otp = request.POST.get('otp')
        if otp == '1234':
            request.user.is_verified = True
            request.user.save()
            messages.success(request, 'OTP verified successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP.')
            return redirect('otpverify')
    return render(request, 'two-factor-auth.html')






def available_routes(request):
    
    allroutes = NewRoute.objects.order_by('-boarding_date').all()

    if request.GET.get('facilities') or request.GET.get('boardingpoint') or request.GET.get('droppingpoints') or request.GET.get('boarding_date'):
        boardingpoint = request.GET.get('boardingpoint')
        droppingpoints = request.GET.get('droppingpoints')
        boarding_date = request.GET.get('boarding_date')
        facility = request.GET.get('facilities')
        if boardingpoint:
            allroutes = allroutes.filter(boarding_point__name=boardingpoint)
        if droppingpoints:
            allroutes = allroutes.filter(route_dropping_points__route_dropping_point__dropping_point__name=droppingpoints)
        
        if boarding_date:
            allroutes = allroutes.filter(boarding_date=boarding_date)

        if facility:
            print(facility)
            allroutes = allroutes.filter(facilites__id=facility)
    
    routes_with_last_dropping = []
    for route in allroutes:
        last_dropping_point = route.get_last_dropping_point()
        travel_duration = route.get_travel_duration()
        try:
            booked_seats = route.booked_seats.split(',')
        except:
            booked_seats = []
        routes_with_last_dropping.append({
            'route': route,
            'last_dropping_point': last_dropping_point,
            'travel_duration': travel_duration,
            'available_seats': int(route.total_seats) - int( len(booked_seats))
        })
    busfacility = BusFacility.objects.all()
    boardingpoint = BoardingPoints.objects.all()
    droppingpoints = DroppingPoints.objects.all()
    
    today = datetime.now().date() 
    current_str = request.GET.get('boarding_date')
    current = None
    if current_str:
        try:
            current = datetime.strptime(current_str, "%Y-%m-%d").date()
        except ValueError:
            # Handle invalid date format
            pass

    if current and current > today:
        tomorrow = current + timedelta(days=1)
        previous = current - timedelta(days=1)
    else:
        tomorrow = today + timedelta(days=1)
        previous = ''
        current = today
    return render(request, 'flight-list-01.html',{'previous':previous,'today':today,'tomorrow':tomorrow,'current':current,'discount':False,'discount_percent':10,'boardingpoint':boardingpoint,'droppingpoints':droppingpoints,'allroutes':routes_with_last_dropping,'busfacility':busfacility})

def view_routes(request,id):
    route = NewRoute.objects.get(id=id)
    last_dropping_point = route.get_last_dropping_point()
    travel_duration = route.get_travel_duration()
    try:
        booked_seats = route.booked_seats.split(',')
    except:
        booked_seats = []
    
    available_seats = route.total_seats - len(booked_seats)
    return render(request, 'Flight-detail.html',{'available_seats':available_seats,'travel_duration':travel_duration,'route':route,'last_dropping_point':last_dropping_point,'discount':False,'discount_percent':10,'booked_seats':booked_seats})






























def about(request):
    return render(request, 'about-us.html')

def gallery(request):
    gallery = Gallery.objects.all()
    return render(request, 'gallery.html',{'gallery':gallery})

def privacy_policies(request):
    return render(request, 'privacy-policy.html')
def terms(request):
    return render(request, 'terms.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        subject = request.POST['subject']
        message = request.POST['message']
        if len(phone) < 10 or len(phone) > 10:
            messages.error(request, 'Please enter a valid phone number.')
            return redirect('contact')
        if not name or not email or not phone or not subject or not message:
            messages.error(request, 'Please enter a valid information.')
            return redirect('contact')
        contact = Contact.objects.create(name=name, email=email, phone=phone, subject=subject, message=message)
        contact.save()
        messages.success(request, 'Your message has been sent successfully.')
        return redirect('contact')
    
    return render(request, 'contact-v1.html')