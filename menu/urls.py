from django.conf.urls import url, patterns
urlpatterns = patterns('menu.views', 
 (r'^merc_signup/?$', 'bus_signup'),
 (r'^merchants/?$', 'bus_signup'),
 (r'^menu/(?P<bid>\d+)/?$', 'fill_menu'),
 (r'^menu/(?P<bid>\d+)/remove/(?P<mid>\d+)/?$', 'delete_menu'),
 (r'^menu/(?P<bid>\d+)/edit/(?P<mid>\d+)/?$', 'edit_menu'),
 )


