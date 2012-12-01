from as2 import settings
from django.conf.urls import url, patterns, include
from django.contrib import admin
from wiki.urls import get_pattern as get_wiki_pattern
from as2.settings import STATIC_URL
from coming_soon.views import survey_detail
admin.autodiscover()
urlpatterns = patterns('',
        url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': STATIC_URL+'img/favicon.ico'}),
                url(r'^admin/', include(admin.site.urls)),
        
        url(r'^/?', include('coming_soon.urls')),
        url(r'^api/', include('api.urls')),
        url(r'^surveys/', include('survey.urls')),
        (r'^wiki/?', get_wiki_pattern()),
    
)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',  {'document_root':     settings.MEDIA_ROOT}),
		(r'^(?P<path>.*)$', 'django.views.static.serve',  {'document_root':     settings.MEDIA_ROOT}),
    )


