from django.test import TestCase
from mainUI.forms import UserForm, ServiceProvidersForm
from mainUI.models import WorkingDays, WorkingPlan
from datetime import datetime

class UserFormTest(TestCase):
    
    # Test if form is valid with valid data
    def test_UserForm_valid(self):
        form = UserForm(data={'username':'testuser', 'email':'user@test.com', 'password':'testuser', 'first_name':'User', 'last_name':'Tester'})
        self.assertTrue(form.is_valid())

    # Test if form is invalid with bad input
    def test_UserForm_invalid(self):
        form = UserForm(data={'username':'', 'email':'user@test.com', 'password':'testuser', 'first_name':'User', 'last_name':'Tester'})
        self.assertFalse(form.is_valid())


# CustomerForm: Using external application that tests validity of phone number input

# DatePickForm: Using external application that tests validity of input