from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from Home.models import *
from RouteDir.models import *
from django.db.models import Prefetch

import json


def dashboard(request):
    
    if request.user.is_superuser:
        return render(request, 'dashboard/index.html')
    return redirect('dashboard_login')

def dashboard_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return redirect('dashboard')
            else:
                messages.error(request, 'You are not authorized to access this page.')
                
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('dashboard_login')
        
    return render(request, 'dashboard/login.html')


def all_users(request):
    if not request.user.is_superuser:
        return redirect('dashboard_login')
    
    if request.GET.get('option') == 'delete':
        id = request.GET.get('id')
        user = User.objects.get(id=id)
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('all-users')
    
    
    
    users = User.objects.order_by('-id').all()
    return render(request, 'dashboard/users-list.html',{'users':users})


def all_routes(request):
    if request.GET.get('option') == 'delete':
        id = request.GET.get('id')
        
        route = RouteDroppingPoint.objects.get(id=id)
        if NewRoute.objects.filter(route_dropping_points=route).exists():
            messages.error(request, 'Route is already assigned to a bus.')
            return redirect('all-routes')
        
        route.delete()
        messages.success(request, 'Route deleted successfully.')
        return redirect('all-routes')
    
    
    
    
    if request.method == 'POST':
        route_list = request.POST.get('dropping_points').split(',')
        name = request.POST.get('name')
        routes = RouteDroppingPoint.objects.create(name=name)
        routes.save()
        for i,item in enumerate(route_list):
            route_core =RouteDroppingPointCore.objects.create(route_name=routes,dropping_point=DroppingPoints.objects.get(id=item),order=i)
            route_core.save()
        messages.success(request,'Added !')
        return redirect('all-routes')    
        
    routes = RouteDroppingPoint.objects.prefetch_related(
        Prefetch('route_dropping_point', queryset=RouteDroppingPointCore.objects.order_by('order'))
    ).all()
    dropping_points = DroppingPoints.objects.order_by('id').all()
    return render(request, 'dashboard/routes-list.html',{'routes':routes,'dropping_points':dropping_points})

def all_boarding_points(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        boarding_point = BoardingPoints.objects.create(name=name)
        boarding_point.save()
        messages.success(request,'Boarding point Added successfully!')
        return redirect('all-boarding-points')
    
    if request.GET.get('option') == 'delete':
        id = request.GET.get('id')
        boarding_point = BoardingPoints.objects.get(id=id)
        if NewRoute.objects.filter(boarding_point=boarding_point).exists():
            messages.error(request,'Boarding point is used in Buse Routes.')
            return redirect('all-boarding-points')
        boarding_point.delete()
        messages.success(request, 'Boarding point deleted successfully.')
        return redirect('all-boarding-points')
    
    
    boarding_points = BoardingPoints.objects.order_by('id').all()
    return render(request, 'dashboard/boarding-points-list.html',{'boarding_points':boarding_points})

def all_dropping_points(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        dropping_point = DroppingPoints.objects.create(name=name)
        dropping_point.save()
        messages.success(request,'Dropping point Added successfully!')
        return redirect('all-dropping-points')
    
    if request.GET.get('option') == 'delete':
        id = request.GET.get('id')
        dropping_point = DroppingPoints.objects.get(id=id)
        if RouteDroppingPointCore.objects.filter(dropping_point=dropping_point).exists():
            messages.error(request,'Dropping point is used in routes.')
            return redirect('all-dropping-points')
        dropping_point.delete()
        messages.success(request, 'Dropping point deleted successfully.')
        return redirect('all-dropping-points')
    
    dropping_points = DroppingPoints.objects.order_by('id').all()
    return render(request, 'dashboard/dropping-points-list.html',{'dropping_points':dropping_points})

def all_facilities(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        facility = BusFacility.objects.create(name=name)
        facility.save()
        messages.success(request,'Facility Added successfully!')
        return redirect('all-facilities')
    
    if request.GET.get('option') == 'delete':
        id = request.GET.get('id')
        facility = BusFacility.objects.get(id=id)
        facility.delete()
        messages.success(request, 'Bus Facility deleted successfully.')
        return redirect('all-facilities')    

    facilities = BusFacility.objects.order_by('id').all()
    
    return render(request, 'dashboard/facilities-list.html',{'facilities':facilities})

def all_bookings(request):
    return render(request, 'dashboard/bookings-list.html')

def all_buses(request):
    if not request.user.is_superuser:
        return redirect('dashboard_login')
    
    
    if request.method == 'POST':
        bus_no  = request.POST.get('bus_no')
        boarding_date = request.POST.get('boarding_date')
        boarding_time = request.POST.get('boarding_time')
        boarding_point = request.POST.get('boarding_point')
        route_dropping_points = request.POST.get('route_dropping_points')
        
        dropping_time = request.POST.get('dropping_time')
        dropping_date = request.POST.get('dropping_date')
        total_seats = request.POST.get('total_seats')
        
        base_price = request.POST.get('base_price')
        
        price_drop_to = request.POST.get('price_drop_to')
        
        facilites = json.loads(request.POST.get('facilities','[]'))
        boarding_date = datetime.strptime(boarding_date, '%Y-%m-%d').date()
        dropping_date = datetime.strptime(dropping_date, '%Y-%m-%d').date()
        boarding_time = datetime.strptime(boarding_time, '%H:%M').time()
        dropping_time = datetime.strptime(dropping_time, '%H:%M').time()
        
        
        newroute = NewRoute.objects.create(
            bus_no = bus_no,
            boarding_date = boarding_date,
            boarding_time = boarding_time,
            boarding_point = BoardingPoints.objects.get(id=boarding_point),
            route_dropping_points = RouteDroppingPoint.objects.get(id=route_dropping_points),
            dropping_time = dropping_time,
            dropping_date = dropping_date,
            total_seats = total_seats,
            base_price = base_price,
            price_drop_to = price_drop_to,

        )
        for i in facilites:
            newroute.facilites.add(BusFacility.objects.get(id=i))
        

        newroute.save()
        
    
        return redirect('bus-info')
    
    
    
    allroutes = NewRoute.objects.order_by('-id').all()
    routes_with_last_dropping = []
    for route in allroutes:
        last_dropping_point = route.get_last_dropping_point()
        travel_duration = route.get_travel_duration()
        try:
            booked_seats = int( len(route.booked_seats.split(',')))
        except:
            booked_seats = 0
        routes_with_last_dropping.append({
            'route': route,
            'last_dropping_point': last_dropping_point,
            'travel_duration': travel_duration,
            'booked_seats': booked_seats,
            
        })
        
    boardingpoint = BoardingPoints.objects.all()
    droppingpoints = DroppingPoints.objects.all()   
    busfacility = BusFacility.objects.all()
    routes =RouteDroppingPoint.objects.all()
    return render(request, 'dashboard/buses-list.html',{'routes':routes,'buses':routes_with_last_dropping,'boardingpoint':boardingpoint,'droppingpoints':droppingpoints,'busfacility':busfacility})


def bus_details(request,id):
    bus= NewRoute.objects.get(id=id)
    
    
    if request.method == 'POST':
        if request.GET.get('option')=='bookedSeats':
            seat_no = request.POST.get('selectedSeats')
            if bus.booked_seats == '' or bus.booked_seats == None:
                bus.booked_seats = f'{seat_no}'
            else:
                bus.booked_seats += f',{seat_no}'
            bus.save()
            messages.success(request, 'Seat booked successfully.')
            return redirect('bus-details',id=id)
        
        
        
        
        
        
        bus_no  = request.POST.get('bus_no')
        boarding_date = request.POST.get('boarding_date')
        boarding_time = request.POST.get('boarding_time')
        boarding_point = request.POST.get('boarding_point')
        route_dropping_points = request.POST.get('route_dropping_points')
        
        dropping_time = request.POST.get('dropping_time')
        dropping_date = request.POST.get('dropping_date')
        total_seats = request.POST.get('total_seats')
        
        base_price = request.POST.get('base_price')
        
        price_drop_to = request.POST.get('price_drop_to')
        
        facilites = request.POST.get('facilities','')
        if facilites:
            facilites = facilites.split(',')
        else:
            facilites = []
            
            
        boarding_date = datetime.strptime(boarding_date, '%Y-%m-%d').date()
        dropping_date = datetime.strptime(dropping_date, '%Y-%m-%d').date()
        boarding_time = datetime.strptime(boarding_time, '%H:%M').time()
        dropping_time = datetime.strptime(dropping_time, '%H:%M').time()
        
        
        bus.bus_no = bus_no
        bus.boarding_date = boarding_date
        bus.boarding_time = boarding_time
        bus.boarding_point = BoardingPoints.objects.get(id=boarding_point)
        bus.route_dropping_points = RouteDroppingPoint.objects.get(id=route_dropping_points)
        bus.dropping_time = dropping_time
        bus.dropping_date = dropping_date
        bus.total_seats = total_seats
        bus.base_price = base_price
        bus.price_drop_to = price_drop_to
        
        for i in bus.facilites.all():
            bus.facilites.remove(i)
        for i in facilites:
            bus.facilites.add(BusFacility.objects.get(id=i))
    
        bus.save()
        messages.success(request, 'Bus details updated successfully')
        return redirect('bus-details',id=id)
    
    try:
        booked_seats = bus.booked_seats.split(',')
    except:
        booked_seats = ['']
    available_seats = int(bus.total_seats) - int( len(booked_seats))
    last_dropping_point = bus.get_last_dropping_point()
    
        
    
    
    boardingpoint = BoardingPoints.objects.all()
    droppingpoints = DroppingPoints.objects.all()   
    busfacility = BusFacility.objects.all()
    routes =RouteDroppingPoint.objects.all()
    facilities = bus.facilites.values_list('id', flat=True)
    facilities_str = ','.join(map(str, facilities)) 
    return render(request, 'dashboard/bus-details.html',{'selected_facilities': facilities_str,'boardingpoint':boardingpoint,'droppingpoints':droppingpoints,'busfacility':busfacility,'routes':routes,'busdetails':True,'bus':bus,"booked_seats":booked_seats,'available_seats':available_seats,'last_dropping_point':last_dropping_point})