from django import forms
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.contrib.auth.models import User
from mainUI.models import ServiceProviders, Customer, Booking


# Form class for django's User model
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 
        'first_name', 'last_name')


# Form class for ServiceProvider model
class ServiceProvidersForm(forms.ModelForm):
  
    class Meta:
        model = ServiceProviders
        exclude = ('user_type', 'user',)


# Form class for Customer model
class CustomerForm(forms.ModelForm):
    
    class Meta:
        model = Customer
        fields = ['customer_phone',]    
        widgets = {'customer_phone': PhoneNumberPrefixWidget()} 
        exclude = ('user_type', 'user',)


# Form class for allowing the user to pick a date
class DatePickForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ['booking_date']
        widgets = {'booking_date': forms.DateTimeInput(attrs={'class': 'datetime-input'})}