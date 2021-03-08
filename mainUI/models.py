from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField


# Working day: a day of the week with working hours
class WorkingDays(models.Model):
    working_day = models.IntegerField()  # 0-Monday to 6-Sunday
    working_day_description = models.CharField(max_length=30)  # the name of the day
    start_hour = models.TimeField()  # the opening hour
    end_hour = models.TimeField()  # the closing hour

    def __str__(self):
            return self.working_day_description + ' ' + str(self.start_hour)+' - ' + str(self.end_hour)

    class Meta:
        verbose_name_plural = 'Working Days Plans'


# Working Plan: is a group of working days that create 
class WorkingPlan(models.Model):
    working_plan_name = models.CharField(max_length=50)
    working_day = models.ManyToManyField(WorkingDays)

    def __str__(self):
            return self.working_plan_name

    class Meta:
        verbose_name = 'Working Hours'
        verbose_name_plural = 'Working Plans'


# ServiceProviders: a Model for service providers
class ServiceProviders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider_businness_name = models.CharField(max_length=128)
    provider_address = models.CharField(max_length=30, verbose_name='Address')
    provider_zipcode = models.CharField(max_length=10, verbose_name='Zip Code')
    working_plan = models.ForeignKey(WorkingPlan, on_delete=models.CASCADE)

    def __str__(self):
            return self.provider_businness_name

    class Meta:
        verbose_name_plural = 'Service Providers'
                

# Category: a model for categorising services
class ServiceCategory(models.Model):
    category_name = models.CharField(max_length=60)

    def __str__(self):
            return self.category_name

    class Meta:
        verbose_name_plural = 'Service Categories'


# Services: a model for the services available
class Services(models.Model):
    service_name = models.CharField(max_length=30)
    
    service_category = models.ManyToManyField(ServiceCategory)
    service_commission = models.FloatField(validators=[MinValueValidator(0.5), MaxValueValidator(99)])

    def __str__(self):
            return self.service_name

    class Meta:
        verbose_name_plural = 'Services'


# Provider services: a Model for services of each provider
class ProviderService(models.Model):
    provider = models.ForeignKey(ServiceProviders, on_delete=models.CASCADE)
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    service_description = models.CharField(max_length=1000)    
    price = models.FloatField(validators=[MinValueValidator(0)])
    duration = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
            return self.provider.provider_businness_name + ' => Service:' + self.service.service_name

    class Meta:
        verbose_name_plural = 'Provider Services'


# Customer: A Model for customers
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_phone = PhoneNumberField()

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name_plural = 'Customers'
    

# Booking: A Model for bookings
class Booking(models.Model):
    booking_request_date = models.DateTimeField(default=datetime.now())  # the date & time the request was made
    booking_date = models.DateTimeField()  # the date & time the booking will be held
    booking_service = models.ForeignKey(Services, on_delete=models.CASCADE)
    booking_provider = models.ForeignKey(ServiceProviders, on_delete=models.CASCADE)
    booking_confirmed = models.BooleanField(default=False)
    booking_canceled = models.BooleanField(default=False)
    booking_excecuted = models.BooleanField(default=False)  # for future use
    booking_charged = models.BooleanField(default=False)  # for future use
    booking_customer = models.ForeignKey(Customer, on_delete=models.CASCADE)    
    
    def __str__(self):
                return self.booking_customer.user.first_name + ' provider: ' + \
                       self.booking_provider.provider_businness_name + ' => Service:' + \
                       self.booking_service.service_name
    
    class Meta:
        verbose_name_plural = 'Bookings'
