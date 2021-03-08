from django.test import TestCase
from django.contrib.auth.models import User
from mainUI.models import WorkingDays, WorkingPlan, ServiceProviders, ServiceCategory, Services, ProviderService, Customer, Booking
from datetime import datetime


# setUpTestData run once to setup non-modified data for all class methods.
# setUp runs once for every test method to setup clean data.
class WorkingDaysTest(TestCase):
    @classmethod
    def setUpTestData(cls):        
        WorkingDays.objects.create(working_day = 0, working_day_description = 'Monday', start_hour= datetime.strptime('08:00:00','%H:%M:%S'), end_hour= datetime.strptime('15:00:00', '%H:%M:%S'))
      
    def test_working_day_label(self):
        workingday = WorkingDays.objects.get(id=1)
        field_label = workingday._meta.get_field('working_day').verbose_name
        self.assertTrue(field_label, 0)

    def test_working_day_description_label(self):
        workingday = WorkingDays.objects.get(id=1)
        field_label = workingday._meta.get_field('working_day_description').verbose_name
        self.assertEquals(field_label, 'working day description')
    
    def test_start_hour_label(self):
        workingday = WorkingDays.objects.get(id=1)
        field_label = workingday._meta.get_field('start_hour').verbose_name
        self.assertEquals(field_label, 'start hour')
        
    def test_end_hour_label(self):
        workingday = WorkingDays.objects.get(id=1)
        field_label = workingday._meta.get_field('end_hour').verbose_name
        self.assertEquals(field_label, 'end hour')

    def test_working_day_description_max_length(self):
        workingday = WorkingDays.objects.get(id=1)
        max_length = workingday._meta.get_field('working_day_description').max_length
        self.assertEquals(max_length, 30)

    def test_to_string_function(self):
        workingday = WorkingDays.objects.get(id=1)
        expected_str = workingday.working_day_description + ' ' +str(workingday.start_hour)+' - '+str(workingday.end_hour)
        self.assertEquals(expected_str, str(workingday))

class WorkingPlanTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        monday = WorkingDays.objects.create(working_day = 0, working_day_description = 'Monday', start_hour= datetime.strptime('08:00:00','%H:%M:%S'), end_hour= datetime.strptime('15:00:00', '%H:%M:%S'))
        tuesday = WorkingDays.objects.create(working_day = 1, working_day_description = 'Tuesday', start_hour= datetime.strptime('08:00:00','%H:%M:%S'), end_hour= datetime.strptime('15:00:00', '%H:%M:%S'))
        wednesday = WorkingDays.objects.create(working_day = 2, working_day_description = 'Wednesday', start_hour= datetime.strptime('08:00:00','%H:%M:%S'), end_hour= datetime.strptime('15:00:00', '%H:%M:%S'))
        thursday = WorkingDays.objects.create(working_day = 3, working_day_description = 'Thursday', start_hour= datetime.strptime('08:00:00','%H:%M:%S'), end_hour= datetime.strptime('15:00:00', '%H:%M:%S'))
        friday = WorkingDays.objects.create(working_day = 4, working_day_description = 'Friday', start_hour= datetime.strptime('08:00:00','%H:%M:%S'), end_hour= datetime.strptime('15:00:00', '%H:%M:%S'))
        
        workingplan = WorkingPlan.objects.create(working_plan_name = 'weekdays')
        workingplan.working_day.add(monday,tuesday,wednesday,thursday,friday)

                
    def test_working_plan_name_label(self):
        workingplan = WorkingPlan.objects.get(id=1)        
        field_label = workingplan._meta.get_field('working_plan_name').verbose_name
        self.assertEquals(field_label, 'working plan name')

    def test_working_plan_to_str(self):
        workingplan = WorkingPlan.objects.get(id=1)
        expected_str = workingplan.working_plan_name
        self.assertEquals(expected_str, str(workingplan))

    def test_working_plan_name_length(self):
        workingplan = WorkingPlan.objects.get(id=1)
        max_length = workingplan._meta.get_field('working_plan_name').max_length
        self.assertEquals(max_length, 50)

    def test_working_days(self):
        workingplan = WorkingPlan.objects.get(id=1)
        days = workingplan._meta.get_field('working_day').verbose_name
        self.assertEquals(days, 'working day')


class CustomerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        testuser = User.objects.create(username='testcustomer', password = 'testcustomer')
        Customer.objects.create(user = testuser, customer_phone = '+447380434844')



    def test_customer_to_str(self):
        customer = Customer.objects.get(id=1)
        expected_str = customer.user.username
        self.assertEquals(expected_str, str(customer))