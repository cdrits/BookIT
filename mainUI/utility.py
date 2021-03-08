from mainUI.models import ServiceProviders, ProviderService, WorkingDays, WorkingPlan, Booking
from datetime import datetime, timedelta
from django.db.models import Q


# Function that checks if the date the customer wants 
# to request a booking is valid; 
# - date in the past
# - whithin working days
# - within working hours
# - not sooner than 30' from present time
# - the provider has another booking at the time
def validateBookingDay(request):
    is_valid = True
    err_msg = ''
    now = datetime.now()
    
    if request:
        # Get date from request 
        booking_datetime = datetime.strptime(request.session['selected_date'], '%Y-%m-%d %H:%M')
        booking_day_id = booking_datetime.weekday()
        booking_date = booking_datetime.date()
        
        # Get provider from request
        provider = ServiceProviders.objects.get(id=request.session['selected_provider'])
        
        # Get service duration from request
        selected_service_id = int(request.session['selected_service'])
        service = ProviderService.objects.get(service_id=selected_service_id, provider_id=provider.id)
        duration = service.duration

        
        # Check if requested date is before now
        if booking_datetime < now:
            is_valid = False
            err_msg = 'Selected date is in the past.'
            return[is_valid, err_msg]

        # Check if requested date is in provider's working days
        try:
            wd = WorkingDays.objects.get(workingplan=provider.working_plan_id, working_day=booking_day_id)
            provider_start_hour = datetime.combine(booking_date, wd.start_hour)
            provider_end_hour = datetime.combine(booking_date, wd.end_hour)
        except WorkingDays.DoesNotExist:
            err_msg = 'Selected date is out of provider\'s working days.'
            is_valid = False
            return[is_valid, err_msg]

        # Check if requested time is within the working hours
        service_end_time = booking_datetime + timedelta(minutes=duration)
        if booking_datetime < provider_start_hour or service_end_time > provider_end_hour:
            is_valid = False
            err_msg = 'Requested time is outside of working hours'
            return[is_valid, err_msg]

        # Check if requested time is 30mins after .now
        min_time = now + timedelta(minutes=30)
        if booking_datetime < min_time:
            is_valid = False
            err_msg = 'Requested time is in less than 30 minutes'
            return[is_valid, err_msg]

        # Check if there is another booking at the time;
        # A query that:
        # checks whether provider has any other confirmed bookings
        # that start or end in the starting time, ending time or duration 
        # of the requested booking
        query =""" 
            select (b.booking_date  + INTERVAL ps.duration  MINUTE) endtime
            , b.* 
            from mainUI_booking b 
            left join mainUI_services s on s.id = b.booking_service_id
            left join mainUI_providerservice ps on ps.provider_id = """ + str(request.session['selected_provider']) + """ and ps.service_id=""" + str(selected_service_id) + """
            Where b.booking_confirmed = 1
            and b.booking_provider_id= """ + str(request.session['selected_provider']) + """
            and b.booking_service_id = """ + str(selected_service_id) + """
            and (b.booking_date between '""" + booking_datetime.strftime("%Y-%m-%d %H:%M") + """' and '""" + service_end_time.strftime("%Y-%m-%d %H:%M")  + """' or 
            b.booking_date + INTERVAL ps.duration  MINUTE between '""" + booking_datetime.strftime("%Y-%m-%d %H:%M") + """' and '""" + service_end_time.strftime("%Y-%m-%d %H:%M")  + """')
                            
            """        
        
        # Store query results in a variable
        b = Booking.objects.raw(query)
               
        # If the query returned something, the provider has 
        # another booking starting, ending or ongoing at the requested date & time
        if b:
            is_valid = False
            err_msg = 'The provider has another booking at that time.'
            return[is_valid, err_msg] 
        
    else:
        is_valid = False
        err_msg = 'No Request passed'
    
    return[is_valid, err_msg]


# Function that reads the email account password from a file
def read_email_pass():
    email_pass = None

    try:
        with open('mailpass.key','r') as f:
            email_pass = f.readline().strip()

    except:
        raise IOError('mailpass.key file not found')

    return email_pass
