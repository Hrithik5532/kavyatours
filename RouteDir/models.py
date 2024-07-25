from django.db import models
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

# Create your models here.

class BoardingPoints(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class DroppingPoints(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class BusFacility(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
  
class RouteDroppingPoint(models.Model):
    name = models.CharField(max_length=100,blank=True, null=True)
    def __str__(self):
        return f" {self.name}"
  
  
class RouteDroppingPointCore(models.Model):
    route_name = models.ForeignKey(RouteDroppingPoint, on_delete=models.CASCADE,related_name='route_dropping_point')
    dropping_point = models.ForeignKey(DroppingPoints, on_delete=models.CASCADE)
    order = models.IntegerField()
    
    class Meta:
        unique_together = ('route_name', 'order')
        ordering = ['order']
        
    def __str__(self):
        return f" {self.dropping_point} (Order: {self.order})"
    

    
class NewRoute(models.Model):
    id = models.CharField(primary_key=True, max_length=4, editable=False, unique=True)
    bus_no = models.CharField(max_length=100, blank=True, null=True)
    boarding_date = models.DateField()
    boarding_time = models.TimeField()
    boarding_point = models.ForeignKey(BoardingPoints, on_delete=models.CASCADE)
    route_dropping_points = models.ForeignKey(RouteDroppingPoint,on_delete=models.CASCADE,null=True,blank=True,related_name='route_dropping_points')
    dropping_time = models.TimeField()
    dropping_date = models.DateField()
    total_seats = models.IntegerField(default=50)
    base_price = models.IntegerField()
    price_drop_to = models.IntegerField()
    
    facilites = models.ManyToManyField(BusFacility)
    booked_seats = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True)

    
    def __str__(self):
        return f"Route from {self.boarding_point} on {self.boarding_date} at {self.boarding_time}"

    def get_last_dropping_point(self):
        return self.route_dropping_points.route_dropping_point.order_by('-order').first()
    
    def get_travel_duration(self):
        # Combine the dates and times into datetime objects
        boarding_datetime = datetime.combine(self.boarding_date, self.boarding_time)
        dropping_datetime = datetime.combine(self.dropping_date, self.dropping_time)
        # Calculate the duration
        duration = dropping_datetime - boarding_datetime
        # Handle cases where the dropping time is the next day
        if duration < timedelta(0):
            duration += timedelta(days=1)
        # Calculate hours and minutes
        hours, remainder = divmod(duration.seconds, 3600)
        minutes = remainder // 60
        return f"{hours} hrs {minutes} mins"

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())[:4]
        super().save(*args, **kwargs)
    


@receiver(pre_save, sender=NewRoute)
def update_status(sender, instance, **kwargs):
    if instance.boarding_date < timezone.now().date():
        instance.status = False



from django.db.models import Max
import re


class PaymentDetails(models.Model):
    id = models.CharField(primary_key=True, max_length=9, editable=False, unique=True)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField(null=True, blank=True)
    customer_phone = models.CharField(max_length=100)
    customer_address = models.CharField(max_length=100,null=True, blank=True)
    
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=100, blank=True, null=True)
    payment_amount = models.CharField(max_length=100, blank=True, null=True)
    
    
    upi_response = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    refunded  = models.BooleanField(default=False)
    
    
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.get_next_id()
        super().save(*args, **kwargs)

    def get_next_id(self):
        # Get the last id in the sequence
        last_id = PaymentDetails.objects.all().aggregate(max_id=Max('id'))['max_id']
        if last_id:
            # Extract the numeric part of the last ID and increment it
            numeric_part = int(re.search(r'\d+', last_id).group())
            next_numeric_part = numeric_part + 1
        else:
            # Start the sequence if no entries exist
            next_numeric_part = 1
        
        # Format the new ID with leading zeros
        next_id = f"P-{next_numeric_part:06d}"
        return next_id
    
    
class BookingDetails(models.Model):
    id = models.CharField(primary_key=True, max_length=9, editable=False, unique=True)
    user = models.ForeignKey('Home.User', on_delete=models.CASCADE)
    bus = models.ForeignKey(NewRoute, on_delete=models.CASCADE)
    payment = models.ForeignKey(PaymentDetails, on_delete=models.CASCADE, null=True, blank=True)
    
    payment_model = models.CharField(max_length=100, blank=True, null=True)
    
    seat_number = models.CharField(max_length=100, blank=True, null=True)
    total_seats = models.IntegerField(default=1)
    total_price = models.IntegerField(default=0)
    base_price = models.IntegerField(default=0)
    
    
    booking_date = models.DateField(auto_now_add=True)
    status = models.BooleanField(default=False)
    
    
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self.get_next_id()
        super().save(*args, **kwargs)

    def get_next_id(self):
        # Get the last id in the sequence
        last_id = BookingDetails.objects.all().aggregate(max_id=Max('id'))['max_id']
        if last_id:
            # Extract the numeric part of the last ID and increment it
            numeric_part = int(re.search(r'\d+', last_id).group())
            next_numeric_part = numeric_part + 1
        else:
            # Start the sequence if no entries exist
            next_numeric_part = 1
        
        # Format the new ID with leading zeros
        next_id = f"B-{next_numeric_part:06d}"
        return next_id
    
    