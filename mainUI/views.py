from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from mainUI.forms import UserForm, ServiceProvidersForm, CustomerForm, DatePickForm
from .models import ProviderService, ServiceCategory, Services, ServiceProviders,\
    WorkingPlan, WorkingDays, Booking, Customer
from django.urls import reverse
from django_tables2 import RequestConfig
from .tables import ServiceProvidersTable, WorkingPlansTable, ProviderPendingBookingsTable,\
    CustomerPendingBookingsTable, ProviderUpcomingBookingsTable, CustomerUpcomingBookingsTable
from .utility import validateBookingDay, read_email_pass
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.core.mail import BadHeaderError, send_mail
from django.db import connection

# View for the homepage
def index(request):
    
    return render(request, 'mainUI/index.html')


# View for the about page
def about(request):

    return render(request, 'mainUI/about.html')


def success_stories(request,id):
           
    return render(request, 'mainUI/success_stories.html', {'id': id})



# View that allows new service providers to register
def register_provider(request):
    # Flag for the template
    registered = False
    
    # If the request method is POST,
    # fetch the data from the user and provider form
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        provider_form = ServiceProvidersForm(data=request.POST)

        if user_form.is_valid() and provider_form.is_valid():
            # Create user
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            # Create provider and associate with user
            provider = provider_form.save(commit=False)
            provider.user = user
            provider.save()
            registered = True
            
            # Log the new user in
            login(request, user)
            
            # Since there are two different types of users,
            # the default registration-redux registration view cannot be used
            # and the user needs to be redirected to the home page manually.            
            # Redirect user to homepage
            return render(request, 'mainUI/index.html')

        else:
            print(user_form.errors, provider_form.errors)
    
    # If it's a GET request, provide user with forms to be filled
    else: 
        user_form = UserForm()
        provider_form = ServiceProvidersForm()

    return render(request, 'registration/provider_registration_form.html', {'user_form': user_form,
                                                                            'provider_form': provider_form,
                                                                            'registered': registered})


# View that allows new customers to register
def register_customer(request):

    # Flag for the template
    registered = False
    
    # If the request method is POST,
    # fetch the data from the user and provider form
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        customer_form = CustomerForm(data=request.POST)

        if user_form.is_valid() and customer_form.is_valid():
            # Create user
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            # Create customer and associate with user
            customer = customer_form.save(commit=False)
            customer.user = user
            customer.save()

            # Log the new user in
            login(request, user)
            registered = True

            # Since there are two different types of users,
            # the default registration-redux registration view cannot be used
            # and the user needs to be redirected to the net page manually.            
            # Redirect user to homepage
            return render(request, 'mainUI/index.html')

        else:
            print(user_form.errors, customer_form.errors)
    
    # If it's a GET request, provide user with forms to be filled
    else: 
        user_form = UserForm()
        customer_form = CustomerForm()

    return render(request, 'registration/customer_registration_form.html', {'user_form': user_form,
                                                                            'customer_form': customer_form,
                                                                            'registered': registered})
 

# View that allows users to see their profiles
@login_required
def user_profile(request):
    
    # Extract the user from the request 
    try:
        user = User.objects.get(username=request.user.username)
    except User.DoesNotExist:
        return render(request, 'mainUI/index.html')
    
    # Determine whether the user is a service provider or a customer
    # Try to relate the User to a ServiceProviders instance.
    # If there is a ServiceProviders instance, it is a service provider, else
    # it is a customer.
    try:
        # Provider variable to be used in the html context
        provider = ServiceProviders.objects.get(user=user)
        context = {
            'user': user,
            'provider': provider    
        }

        # If it is a service provider, show the corresponding profile page
        return render(request, 'mainUI/provider_profile.html', context)
    
    # If the user is a customer
    except ServiceProviders.DoesNotExist:
        # Customer variable to be used in the html context        
        customer = Customer.objects.get(user=user)

        context = {
            'user': user,
            'customer': customer,
            
        }

        # If it is a customer, show the corresponding profile page
        return render(request, 'mainUI/customer_profile.html', context)


# View that allows users to see their pending booking requests
@login_required
def pending_bookings(request):

    try:
        user = User.objects.get(username=request.user.username)
    except User.DoesNotExist:
        return render(request, 'mainUI/index.html')
    
    # Determine whether the user is a service provider or a customer
    # Try to relate the User to a ServiceProviders instance.
    # If there is a ServiceProviders instance, it is a service provider, else
    # it is a customer.
    try:
        # Provider variable to be used in the html context
        provider = ServiceProviders.objects.get(user=user)

        # Create a table that contains the provider's pending booking requests
        table = ProviderPendingBookingsTable(
            Booking.objects.filter(booking_provider=provider,  booking_confirmed=0, booking_canceled=0,
                                   booking_date__gte=datetime.strftime(datetime.now(),
                                                                       '%Y-%m-%d %H:%M:%S')).order_by('booking_date'))
        table.paginate(page=request.GET.get('page', 1), per_page=15)
        
        context = {
            'provider': provider,
            'table': table,
        }

    # If the user is a customer
    except ServiceProviders.DoesNotExist:
        # Customer variable to be used in the html context 
        customer = Customer.objects.get(user=user)
        
        # Create a table that contains the provider's pending booking requests
        table = CustomerPendingBookingsTable(
            Booking.objects.filter(booking_customer=customer, booking_confirmed=0, booking_canceled=0,
                                   booking_date__gte=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))
            .order_by('booking_date'))
        table.paginate(page=request.GET.get('page', 1), per_page=15)
        
        context = {
            'customer': customer,
            'table': table,
        }

    return render(request, 'mainUI/pending_bookings.html', context)


# View that allows users to see their upcoming bookings
@login_required
def upcoming_bookings(request):
    try:
        user = User.objects.get(username=request.user.username)
    except User.DoesNotExist:
        return render(request, 'mainUI/index.html')
 
    # Determine whether the user is a service provider or a customer
    # Try to relate the User to a ServiceProviders instance.
    # If there is a ServiceProviders instance, it is a service provider, else
    # it is a customer.
    try:
        # Provider variable to be used in the html context
        provider = ServiceProviders.objects.get(user=user)
        
        # Create a table that contains the provider's upcoming bookings
        table = ProviderUpcomingBookingsTable(
            Booking.objects.filter(booking_provider=provider,
                                   booking_confirmed=1,
                                   booking_canceled=0,
                                   booking_date__gte=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))
            .order_by('booking_date'))
        table.paginate(page=request.GET.get('page', 1), per_page=15)
        
        context = {
            'provider': provider,
            'table': table,
        }

    # If the user is a customer
    except ServiceProviders.DoesNotExist:
        # Customer variable to be used in the html context
        customer = Customer.objects.get(user=user)
        
        # Create a table that contains the customer's upcoming bookings
        table = CustomerUpcomingBookingsTable(
            Booking.objects.filter(booking_customer=customer,
                                   booking_confirmed=1,
                                   booking_canceled=0,
                                   booking_date__gte=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))
            .order_by('booking_date'))
        table.paginate(page=request.GET.get('page', 1), per_page=15)
        
        context = {
            'customer': customer,
            'table': table,
        }

    return render(request, 'mainUI/upcoming_bookings.html', context)


# View to display available service categories
def srvgroups(request):
    # Get service categories from the database
    cat_services = ServiceCategory.objects.all()[:10]

    context = {
        'title': 'Service Categories',
        'subtitle': 'Select a service category to see available services!',
        'services': cat_services
    }     
    return render(request, 'mainUI/srvgroups.html', context)


# View to display available services for the selected category
def availablesrv(request, id):
    
    # Save selected service category in session
    request.session['selected_srvgroup'] = id
    
    # Get available services of the selected category from the database
    booking_services = Services.objects.filter(service_category=id)

    context = {
        'title': 'Available Services',
        'subtitle': 'Select a service to see available providers!',
        'services': booking_services
    }

    return render(request,'mainUI/availablesrv.html', context)


# View to display service providers for the selected service
def srvproviders(request, id):

    # Save the selected service in session
    request.session['selected_service'] = id

    # Get the provider-services with the selected service-id from the database
    providers_srv = ProviderService.objects.filter(service=id).distinct()
    
    # For the provider-services, find the provider 
    # and add the provider's id to a list
    sprovider=[]
    for p in providers_srv:
        sprovider.append(p.provider_id)

    # Create a table with the service providers
    table = ServiceProvidersTable(ServiceProviders.objects.filter(id__in=sprovider))
    RequestConfig(request).configure(table)

    context = {
        'title': 'Available Providers',
        'subtitle': 'Select a service provider to pick a date!',
        'table': table,
        'selected_cat': request.session['selected_srvgroup'],
    } 

    return render(request, 'mainUI/srvproviders.html', context)


# View to allow customers select a date
def select_date(request, id):

    # Save selected provider in session
    request.session['selected_provider'] = id
    
    # Variable to hold the error message, if any
    err_msg = ''
    
    # Create a form for the user to pick a date
    select_date_form = DatePickForm()
    
    # If it is a post request, get user input from the form
    if request.method == 'POST':
        select_date_form = DatePickForm(data=request.POST)
        
        if select_date_form.is_valid():
            
            # Get selected date from the form
            selected_date = select_date_form['booking_date'].value()
            # Save selected date in session
            request.session['selected_date'] = selected_date       
            
            # Validate Date
            v = validateBookingDay(request)
            # Save results of validation method
            is_valid = v[0]
            err_msg = v[1]

            # If the date the user selected is available, 
            # proceed to confirmation page
            if is_valid:
                request.session['date_status'] = err_msg

                return render(request, 'mainUI/confirmation.html')
            
        else:
            print(select_date_form.errors)

    # If it's a GET request, provide user with forms to be filled
    else:
        select_date_form = DatePickForm()
    
    return render(request, 'mainUI/select_date_form.html',
                  {'datepick_form': select_date_form,
                   'selected_service': request.session['selected_service'],
                   'msg': err_msg,
                   'title': 'Pick a date!',
                    'subtitle': 'Select a date and time and see if it is available!',})


# View that allows customers to request a booking
@login_required
def request_booking(request):

    if request.user.is_authenticated:   
   
        # Test if the logged in user is a customer or a provider;
        # If it is a provider, show error message
        try: 
            customer = Customer.objects.get(user=request.user.id)
        except Customer.DoesNotExist:
            msg = 'You cannot make a booking as a service provider. Please Login/Register as a Customer. Thank you!'
            return render(request, 'mainUI/request_sent.html', {'msg': msg})


        # TO-DO: Check if user has another booking at the date and time


        # Make booking
        booking = Booking()

        booking.booking_date = datetime.strptime(request.session['selected_date'], '%Y-%m-%d %H:%M')
        booking.booking_customer = customer 
        booking.booking_service = Services.objects.get(id=int(request.session['selected_service']))
        booking.booking_provider = ServiceProviders.objects.get(id=int(request.session['selected_provider']))
        booking.save()
        
        # Informative message to the user
        msg = 'Your request has been sent to the provider! Thank you for using bookIT!'
        context = {
            'msg': msg,
            'service': booking.booking_service,
            'provider': booking.booking_provider,
            'date': datetime.strftime(booking.booking_date, '%A, %d %B %Y'),
            'time': datetime.strftime(booking.booking_date, '%H:%M'),
            'confirmed': 'Pending',        
        }
        
        # Send email to provider
        subject = 'You have a new bookIT request!'
        provider = ServiceProviders.objects.get(id=int(request.session['selected_provider']))
        provider_user = User.objects.get(id=provider.user_id)
        provider_email = provider_user.email
        message = str(request.user.username) + ' wants to book an appointment with you!\n' +\
            'Booking details\nService: ' + str(booking.booking_service) + \
            '\nBooking Date: ' + str(booking.booking_date) + \
            '\n\n Please accept or decline the booking in your bookIT profile!'
      
        send_mail(subject, message, from_email='bookitcommunications@hotmail.com', auth_password=read_email_pass(),
                  recipient_list=[provider_email, ])

    else:
        print('User is not authenticated')

    return render(request, 'mainUI/request_sent.html', context)


@login_required
def confirm_booking(request, id):
    
    confirmation_update_query =""" 
            update mainUI_booking 
            set booking_confirmed = 1
            where id= """ + str(id) + """
                
            """    

    cursor = connection.cursor()
    cursor.execute(confirmation_update_query)

    # Information from the booking that was confirmed    
    provider = ServiceProviders.objects.get(user_id=int(request.user.id))    
    booking = Booking.objects.get(id=id)    
    service = ProviderService.objects.filter(provider_id=booking.booking_provider_id).get(service_id = booking.booking_service_id)
    service_id = booking.booking_service_id
    booking_date = booking.booking_date
    booking_duration = service.duration
    booking_end_time = booking_date + timedelta(minutes=booking_duration)
    
    # Notify customer about confirmed booking
    customer = Customer.objects.get(id=booking.booking_customer_id)
    customer_email = User.objects.get(id=customer.user_id).email
    subject = 'Your booking has been confirmed!'
    message = str(customer.user.first_name) + ' your booking with ' + provider.provider_businness_name + ' has been confirmed!' +\
        '\n\nBooking details\nService: ' + str(booking.booking_service) + \
        '\nBooking Date: ' + str(booking.booking_date)
           
    send_mail(subject, message, from_email='bookitcommunications@hotmail.com', auth_password=read_email_pass(),
              recipient_list=[customer_email, ])



    # Cancel bookings that would conflict: 
    # get the conflincting bookings ids with a query 
    # and then decline these bookings with an update_query

    # query: returns the ids of conflicting bookings and information for emailing the users
    query = """select b.id, b.booking_date, u.email, u.first_name, s.service_name
    from mainUI_booking b 
    left join mainUI_services s on s.id = b.booking_service_id
    left join mainUI_customer c on c.id = b.booking_customer_id
    left join auth_user u on u.id = c.user_id 
    left join mainUI_providerservice ps on ps.provider_id = """ + str(provider.id) + """ and ps.service_id=""" + str(service_id) + """
    Where b.booking_confirmed = 0 
    and b.booking_canceled = 0
    and b.booking_provider_id= """ + str(provider.id) + """
    and b.booking_service_id = """ + str(service_id) + """
    and (b.booking_date between '""" + booking_date.strftime("%Y-%m-%d %H:%M") + """' and '""" + booking_end_time.strftime("%Y-%m-%d %H:%M")  + """' or 
    b.booking_date + INTERVAL ps.duration  MINUTE between '""" + booking_date.strftime("%Y-%m-%d %H:%M") + """' and '""" + booking_end_time.strftime("%Y-%m-%d %H:%M")  + """')
                    
    """
    
    # Make an SQL compatible string with the ids of the bookings that need to be updated (to be used in the update_query)
    idstr = "("  # SQL compatible string for the update query
        
    # Debugging
    q = Booking.objects.raw(query)
    
    # If there are any conflicts
    if q:
        # For each booking id returned
        for b in Booking.objects.raw(query):
            # add declined booking id and a comma in the idstr
            idstr += str(b.id) + ","  
            
            # send email to customer
            subject = 'Your booking has been declined.'
            message = str(b.first_name) + ' your booking request for ' + str(b.service_name) + ' with ' + str(provider) + ' has been declined.' +\
                '\n\nBooking details\nService: ' + str(b.service_name) + \
                '\nBooking Date: ' + str(b.booking_date) +\
                '\nBooking Status: DECLINED by the provider'

            send_mail(subject, message, from_email='bookitcommunications@hotmail.com', auth_password=read_email_pass(),
                    recipient_list=[b.email, ])

        # Remove the last comma and put in place a parenthesis to match SQL Syntax requirements
        idstr = idstr[0:len(idstr)-1]   
        idstr +=")"
        
        # Decline conflicting bookings
        update_query = """ 
                update mainUI_booking 
                set booking_canceled = 1
                where id in """ + idstr + """
                    
                """  
        cursor = connection.cursor()
        cursor.execute(update_query)

    
    return pending_bookings(request)


@login_required
def decline_booking(request, id):

    decline_update_query =""" 
            update mainUI_booking 
            set booking_canceled = 1
            where id= """ + str(id) + """
                
            """    

    cursor = connection.cursor()
    cursor.execute(decline_update_query)
     
    # Send email
        
    booking = Booking.objects.get(id=id)
    provider = ServiceProviders.objects.get(user=request.user.id)
    customer = Customer.objects.get(id=booking.booking_customer_id)
    customer_email = User.objects.get(id=customer.user_id).email
    subject = 'Your booking has been declined.'
    message = str(customer.user.first_name) + ' your booking request for ' + str(booking.booking_service) + ' with ' + str(provider) + ' has been declined.' +\
        '\n\nBooking details\nService: ' + str(booking.booking_service) + \
        '\nBooking Date: ' + str(booking.booking_date) +\
        '\nBooking Status: DECLINED by the provider'

    send_mail(subject, message, from_email='bookitcommunications@hotmail.com', auth_password=read_email_pass(),
              recipient_list=[customer_email, ])

    return pending_bookings(request)    


@login_required
def cancel_booking(request, id):

    cancel_update_query =""" 
        update mainUI_booking 
        set booking_canceled = 1
        where id= """ + str(id) + """
            
        """
    cursor = connection.cursor()
    cursor.execute(cancel_update_query)

    # Send email
    booking = Booking.objects.get(id=id)
    # If the booking was canceled by the provider
    try:
        provider = ServiceProviders.objects.get(user=request.user.id)
        customer = Customer.objects.get(id=booking.booking_customer_id)
        customer_email = User.objects.get(id=customer.user_id).email
        subject = 'Your booking has been canceled.'
        message = str(customer.user.first_name) + ' your booking for' + str(booking.booking_service) + ' with ' + str(provider) + ' has been declined.' +\
            '\n\nBooking details\nService: ' + str(booking.booking_service) + \
            '\nBooking Date: ' + str(booking.booking_date) +\
            '\nBooking Status: CANCELED by the provider'
        
        send_mail(subject, message, from_email='bookitcommunications@hotmail.com', auth_password=read_email_pass(),
            recipient_list=[customer_email, ])
    
    # If the booking was canceled by the customer
    except ServiceProviders.DoesNotExist:
        customer = Customer.objects.get(user=request.user.id)
        provider = ServiceProviders.objects.get(id=booking.booking_provider_id)
        provider_email = User.objects.get(id=provider.user_id).email
        subject = 'Your booking has been canceled.'
        message = str(provider.user.first_name) + ' your booking for' + str(booking.booking_service) + ' with ' + str(customer) + ' has been declined.' +\
            '\n\nBooking details\nService: ' + str(booking.booking_service) + \
            '\nBooking Date: ' + str(booking.booking_date) +\
            '\nBooking Status: CANCELED by the customer'
        
        send_mail(subject, message, from_email='bookitcommunications@hotmail.com', auth_password=read_email_pass(),
            recipient_list=[provider_email, ])
    
    return upcoming_bookings(request)   