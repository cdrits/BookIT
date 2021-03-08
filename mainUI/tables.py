import django_tables2 as tables
from .models import ServiceProviders,WorkingDays, Booking


# Table to display ServiceProviders
class ServiceProvidersTable(tables.Table):
    provider_businness_name = tables.TemplateColumn(verbose_name="Provider" ,template_name='mainUI/provider_selection.html')
    
    class Meta:
        model = ServiceProviders
        fields = ('provider_businness_name', 'provider_address', 'provider_zipcode', 'working_plan')


# Table to display WorkingPlans
class WorkingPlansTable(tables.Table):
    class Meta:
        model = WorkingDays


# Table to display pending bookings for providers
class ProviderPendingBookingsTable(tables.Table):

    # TemplateColumns to display images for accepting and declining booking requests
    btnConfirm = tables.TemplateColumn(verbose_name="", template_name="mainUI/btnConfirm.html")  
    btnDecline = tables.TemplateColumn(verbose_name="", template_name="mainUI/btnDecline.html")  
    class Meta:
        model = Booking
        fields = ('booking_date', 'booking_customer', 'booking_request_date')
        

# Table to display pending bookings for customers
class CustomerPendingBookingsTable(tables.Table):
    booking_confirmed = tables.BooleanColumn(verbose_name= 'Status', yesno='Confirmed, Pending Confirmation')
    class Meta:
        model = Booking
        fields = ('booking_date', 'booking_provider', 'booking_request_date', 'booking_confirmed')


# Table to display upcoming bookings for providers
class ProviderUpcomingBookingsTable(tables.Table):
    btnCancel = tables.TemplateColumn(verbose_name="", template_name="mainUI/btnCancel.html")  
    class Meta:
        model = Booking
        fields = ('booking_date', 'booking_service', 'booking_customer')


# Table to display upcoming bookings for providers
class CustomerUpcomingBookingsTable(tables.Table):
    btnCancel = tables.TemplateColumn(verbose_name="", template_name="mainUI/btnCancel.html")  
    class Meta:
        model = Booking
        fields = ('booking_date', 'booking_service', 'booking_provider')