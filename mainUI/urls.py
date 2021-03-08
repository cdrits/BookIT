from django.conf.urls import url,include
from . import views

app_name = 'mainUI'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/', views.about, name='about'),
    url(r'^success_stories/(?P<id>\d+)/$', views.success_stories, name='success_stories'),
    url(r'^register-provider$', views.register_provider, name='register_provider'),
    url(r'^register-customer$', views.register_customer, name='register_customer'),
    url(r'^srvgroups/',views.srvgroups, name='srvgroups'),
    url(r'^availablesrv/(?P<id>\d+)/$',views.availablesrv, name='availablesrv'),
    url(r'^srvproviders/(?P<id>\d+)/$',views.srvproviders, name='srvproviders'),
    url(r'^selectdate/(?P<id>\d+)/$', views.select_date, name='select_date'),
    url(r'^confirmation/(?P<id>\d+)/$', views.select_date, name='select_date'),
    url(r'^request_booking/$', views.request_booking, name='request_booking'),
    url(r'^request_sent/$', views.request_booking, name='request_sent'),
    url(r'^user_profile/$', views.user_profile, name='user_profile'),
    url(r'^pending_bookings/$', views.pending_bookings, name='pending_bookings'),
    url(r'^upcoming_bookings/$', views.upcoming_bookings, name='upcoming_bookings'),
    url(r'^confirm_booking/(?P<id>\d+)/$', views.confirm_booking, name='confirm_booking'),
    url(r'^decline_booking/(?P<id>\d+)/$', views.decline_booking, name='decline_booking'),
    url(r'^cancel_booking/(?P<id>\d+)/$', views.cancel_booking, name='cancel_booking'),

]