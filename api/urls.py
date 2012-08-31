from django.conf.urls import url, patterns

urlpatterns = patterns('api.views',
    (r'^populate_database/?$','prepopulate_database'),
    
    
    
    (r'^businesses/?$', 'get_businesses'),
    (r'^businesses/search/?$', 'search_businesses'),

    (r'^businesses/query/(?P<oid>\d+)/?$', 'query_businesses'),

    (r'^business/(?P<oid>\d+)/?$', 'get_business'),
    (r'^business/add/?$', 'add_business'),
    (r'^business/remove/(?P<oid>\d+)/?$', 'remove_business'),
    (r'^business/edit/(?P<oid>\d+)/?$', 'edit_business'),
    (r'^business/rate/(?P<oid>\d+)/?$', 'rate_business'),
    
    #returns the categories associated  with a business
    (r'^business/topics/(?P<oid>\d+)/?$', 'get_business_topics'),
    (r'^business/topic/(?P<oid>\d+)/?$', 'get_business_topic'),
    (r'^business/topic/add/(?P<oid>\d+)/?$', 'add_business_topic'),
    (r'^business/topic/remove/(?P<oid>\d+)/?$', 'remove_business_topic'),
    (r'^business/topic/rate/(?P<oid>\d+)/?$', 'rate_business_topic'),

    (r'^business/types/(?P<oid>\d+)/?$', 'get_business_types'),
    (r'^business/type/add/(?P<oid>\d+)/?$', 'add_business_type'),
    (r'^business/type/remove/(?P<oid>\d+)/?$', 'remove_business_topic'),
    
    (r'^types/?', 'get_types'),
    (r'^type/add/?', 'add_type'),
    (r'^type/(?P<oid>\d+)/?', 'get_type'),

    
    (r'^all_topics/?$', 'get_topics'),
    (r'^topics/?$', 'get_topics_parent'),
    (r'^topic/(?P<oid>\d+)/?$', 'get_topic'),
    (r'^topic/subscribe/(?P<oid>\d+)/?$', 'subscribe_topic'),
    (r'^topic/unsubscribe/(?P<oid>\d+)/?$', 'unsubscribe_topic'),
    (r'^topics/?$', 'get_topics'),
    (r'^topic/(?P<oid>\d+)/?$', 'get_topic'),
    #(r'^topic/add/?$', 'add_topic'),


   #currently not designed / implemented    
   # (r'^comments/?$', 'get_comment'),
    (r'^comment/(?P<oid>\d+)/?$', 'get_comment'),
    (r'^comment/add/?$', 'add_comment'),
    (r'^comment/remove/?$', 'remove_comment'),
    (r'^comment/rate/(?P<oid>\d+)/?$', 'rate_comment'),
    (r'^comment/edit/(?P<oid>\d+)/?$','edit_comment'),
    
    url(r'^photos/all/?$', 'get_all_photos'),
    (r'^photos/(?P<oid>\d+)/?$', 'get_photos'),
    (r'^photo/(?P<oid>\d+)/?$', 'get_photo'),
    (r'^photo/add/?$', 'add_photo'),
    (r'^photo/remove/(?P<oid>\d+)/?$', 'remove_photo'),
    (r'^photo/edit/(?P<oid>\d+)/?$', 'edit_photo'),
    (r'^photo/rate/(?P<oid>\d+)/?$', 'rate_photo'),

    (r'^query/base/?$', 'get_query_base'),
    (r'^queries/?$', 'get_queries'),
    (r'^query/(?P<oid>\d+)/?$', 'get_query'),
    (r'^query/remove/(?P<oid>\d+)/?$', 'get_query'),
    (r'^query/add/?$', 'add_query'),
    (r'^query/edit/(?P<oid>\d+)/?$', 'edit_query'), 



    (r'^user/?$', 'get_user'),
    (r'^user/update/?$', 'update_user')



)

