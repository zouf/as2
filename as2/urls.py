from as2 import settings
from django.conf.urls import url, patterns, include
from django.contrib import admin
from wiki.urls import get_pattern as get_wiki_pattern


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('api.urls')),
    
    (r'^wiki/?', get_wiki_pattern()),
    url(r'^/?$', 'coming_soon.views.index'),

    url(r'^business/(?P<oid>\d+)/?$', 'coming_soon.views.detail'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',  {'document_root':     settings.MEDIA_ROOT}),
		(r'^(?P<path>.*)$', 'django.views.static.serve',  {'document_root':     settings.MEDIA_ROOT}),
    )


