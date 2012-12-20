from django.conf.urls import url, patterns
urlpatterns = patterns('menu.views', 
 (r'^merc_signup/?$', 'bus_signup'),
 (r'^merchants/?$', 'bus_signup'),
 (r'^menus/?$', 'get_menulist'),
 (r'^menu/(?P<bid>\d+)/?$', 'get_edit_menu'),
 (r'^menu/(?P<bid>\d+)/edit/?$', 'get_edit_business'),
 (r'^menu/(?P<bid>\d+)/remove/(?P<mid>\d+)/?$', 'delete_menu'),
 (r'^menu/(?P<bid>\d+)/details/(?P<mid>\d+)/?$', 'get_edit_details'),
 )


