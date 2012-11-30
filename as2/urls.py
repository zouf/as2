from as2 import settings
from django.conf.urls import url, patterns, include
from django.contrib import admin
from wiki.urls import get_pattern as get_wiki_pattern
from as2.settings import STATIC_URL

admin.autodiscover()

urlpatterns = None
urlpatterns = patterns('',
        url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': STATIC_URL+'img/favicon.ico'}),
        url(r'^/?$', 'coming_soon.views.coming_soon'),
        url(r'^health/?$', 'coming_soon.views.health_survey'), 
        url(r'^learn/?$', 'coming_soon.views.learn'), 
        url(r'^contact/?$', 'coming_soon.views.contact'), 
        url(r'^merchants/?$', 'coming_soon.views.merchants'), 
        url(r'^about/?$', 'coming_soon.views.about'), 
        url(r'^allergy/?$', 'coming_soon.views.health_survey'), 

        url(r'^admin/', include(admin.site.urls)),
        
        url(r'^api/', include('api.urls')),
        (r'^wiki/?', get_wiki_pattern()),
    
)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',  {'document_root':     settings.MEDIA_ROOT}),
		(r'^(?P<path>.*)$', 'django.views.static.serve',  {'document_root':     settings.MEDIA_ROOT}),
    )


