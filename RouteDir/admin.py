from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(BoardingPoints)
admin.site.register(DroppingPoints)
admin.site.register(NewRoute)
admin.site.register(BusFacility)
admin.site.register(RouteDroppingPoint)
admin.site.register(RouteDroppingPointCore)


admin.site.register(BookingDetails)
admin.site.register(PaymentDetails)
