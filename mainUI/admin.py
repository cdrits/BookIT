from django.contrib import admin
from .models import ServiceCategory,ServiceProviders,Services,ProviderService,WorkingDays,WorkingPlan,Customer, Booking

# Register your models here.

admin.site.register(ServiceCategory)
admin.site.register(Services)
admin.site.register(ServiceProviders)
admin.site.register(ProviderService)
admin.site.register(WorkingDays)
admin.site.register(WorkingPlan)
admin.site.register(Customer)
admin.site.register(Booking)