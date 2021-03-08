from django.test import TestCase
from django.urls import reverse
from mainUI.models import ProviderService, ServiceCategory, Services, ServiceProviders,\
    WorkingPlan, WorkingDays, Booking, Customer

class SrvgroupsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        catnum = 10
        for i in range(catnum):
            ServiceCategory.objects.get_or_create(category_name = f'Test Category {i}')
            
        
    def test_view_url_exists_at_desired_location(self): 
        response = self.client.get('/mainUI/srvgroups/') 
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('mainUI:srvgroups'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('mainUI:srvgroups'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainUI/tpl_availablesrv.html')
        self.assertTemplateUsed(response, 'mainUI/srvgroups.html')

    def test_lists_all_service_categories(self):        
        response = self.client.get(reverse('mainUI:srvgroups'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['services']) == 10)